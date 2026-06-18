<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auto_dev-ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/auto_dev-ioctl.h

## Purpose
Defines the modern autofs control-device ioctl ABI used to manage autofs mount points through `/dev/autofs`.

## Important APIs, Types, And Functions
`struct autofs_dev_ioctl` is the common extensible payload with version, size, `ioctlfd`, command union, and optional path tail. Argument structs cover protocol version, openmount, ready/fail tokens, pipe fd, timeout, requester, expire, askumount, and mountpoint query. Ioctls include version/proto queries, open/close mount, ready/fail, setpipefd/catatonic, timeout, requester, expire, askumount, and ismountpoint.

## Control Flow
Userspace initializes the struct with `init_autofs_dev_ioctl`, optionally appends a path, opens or targets a mount fd, and issues command-specific ioctls. Kernel autofs uses tokens to complete pending mount/expire requests and returns mount/requester/status data through the union.

## State And Persistence
State is per autofs mount and control fd: protocol version, pipe fd, pending wait tokens, timeout, requester uid/gid, expiration candidates, and mountpoint identity. It is runtime mount state.

## Dependencies And Integration Points
Depends on `auto_fs.h` and string helpers. Integrates with automount daemons, VFS mount handling, pipes, and path-based control operations.

## Risks And Edge Cases
The `size` must include appended path data, version/size negotiation matters, token mismatch can leave waiters blocked, and `ioctlfd` defaults to -1. Path validation and mount namespace context are critical.

## Test Signals
Initialize/version tests, openmount/closemount, ready/fail token completion, setpipefd/catatonic behavior, timeout get/set, requester query, expire/askumount, ismountpoint, and malformed size/path rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auto_dev-ioctl.h -->
