# sources/distributed-fs/ceph-client/fs/fuse/ioctl.c

## Purpose
Implements FUSE file ioctl handling, including normal and compat ioctls, CUSE-compatible retry iovec marshalling, fs-verity special argument setup, and private ioctl helpers used by file attribute get/set operations.

## Important APIs, Types, And Functions
`fuse_do_ioctl()` is the exported core that builds `FUSE_IOCTL` requests, copies user iovec payloads into temporary folios, handles server `FUSE_IOCTL_RETRY`, and copies reply data back to user buffers. `fuse_ioctl_common()`, `fuse_file_ioctl()`, and `fuse_file_compat_ioctl()` provide VFS-facing wrappers with access and bad-inode checks. `fuse_send_ioctl()` centralizes request submission and translates `-ENOSYS` to `-ENOTTY`. `fuse_copy_ioctl_iovec_old()` supports legacy pre-minor-16 iovec ABI and compat iovec layout. `fuse_copy_ioctl_iovec()` validates modern `struct fuse_ioctl_iovec` base/length values and compat truncation. `fuse_setup_measure_verity()` and `fuse_setup_enable_verity()` derive correct iovec lengths and extra salt/signature user buffers for fs-verity ioctls. `fuse_priv_ioctl()`, `fuse_priv_ioctl_prepare()`, and cleanup helpers open a temporary FUSE file handle for internal file-attribute ioctls. `fuse_fileattr_get()` and `fuse_fileattr_set()` adapt VFS fileattr APIs to `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_IOC_FSGETXATTR`, and `FS_IOC_FSSETXATTR`.

## Control Flow
Restricted ioctls initialize in/out iovecs from `_IOC_DIR` and `_IOC_SIZE`; unrestricted ioctls start with no deep-copy areas and allow the server to request retry iovecs. `fuse_do_ioctl()` allocates folio buffers up to `fc->max_pages`, copies requested input user memory, sends a `FUSE_IOCTL` request, and either retries after parsing returned iovecs or finalizes by copying output pages into user memory. Retry paths verify iovec count and cumulative lengths before looping. Private fileattr ioctls take a temporary open reference, submit a simple non-retry ioctl, and release the file.

## State And Persistence
The file itself stores no persistent filesystem state. It mutates request-local `fuse_args_pages`, folio arrays, and `outarg.result`. File attribute operations may persist remote filesystem state through the userspace server. `FUSE_IOCTL_32BIT`, `FUSE_IOCTL_COMPAT`, `FUSE_IOCTL_DIR`, and fs-verity-derived iovecs define ABI-visible request state.

## Dependencies And Integration Points
Depends on FUSE request infrastructure in `fuse_i.h`, page/folio allocation, `iov_iter`, Linux compat ABI helpers, `fileattr`, and fs-verity ioctl structures. Exports `fuse_do_ioctl()` for use elsewhere in FUSE. Integrates with VFS ioctl and fileattr operations and with userspace FUSE/ CUSE servers.

## Risks
Iovec validation is security-critical because server-provided retry vectors drive user-memory copying. Overflow checks in `fuse_verify_ioctl_iov()` and max page enforcement are important DoS boundaries. Compat ABI handling can reject valid-looking data when client/server bitness assumptions mismatch. Restricted mode deliberately forbids retry; accepting retry there would allow excessive deep-copy authority. fs-verity salt/signature sizes are capped at 256 pages to bound memory use.

## Test Signals
Exercise normal ioctl, compat ioctl, restricted and unrestricted retry, malformed iovec sizes, excessive iovec lengths, `ENOSYS` translation to `ENOTTY`, fs-verity measure/enable with and without salt/signature, and fileattr get/set paths against a FUSE server that records request fields.
