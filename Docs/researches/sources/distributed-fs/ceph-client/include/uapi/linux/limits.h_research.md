# sources/distributed-fs/ceph-client/include/uapi/linux/limits.h

Purpose: exposes core Linux userspace limit constants for file descriptors, groups, argument length, path/name lengths, pipe atomicity, xattr sizes, and real-time signal count.

Important APIs and types: constants include `NR_OPEN`, `NGROUPS_MAX`, `ARG_MAX`, `LINK_MAX`, `MAX_CANON`, `MAX_INPUT`, `NAME_MAX`, `PATH_MAX`, `PIPE_BUF`, `XATTR_NAME_MAX`, `XATTR_SIZE_MAX`, `XATTR_LIST_MAX`, and `RTSIG_MAX`.

Control flow: there is no executable flow. User and kernel headers include these constants when validating buffers, path lengths, pipe writes, group arrays, and xattr data.

State and persistence: no state. The constants shape ABI expectations and buffer sizing.

Dependencies and integration points: standalone UAPI header used by libc, tools, filesystems, xattr consumers, shell/runtime code, and kernel UAPI consumers.

Risks and test signals: risks are changing values that applications compile into fixed buffers, and mismatch with libc `limits.h` or runtime sysconf behavior. Test by compiling representative userspace headers, checking xattr boundary tests, path/name limit tests, pipe atomic write behavior, and group/exec argument limit validation.
