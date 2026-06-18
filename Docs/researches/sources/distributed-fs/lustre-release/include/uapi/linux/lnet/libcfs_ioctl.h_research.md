# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/libcfs_ioctl.h

Purpose: low-level ioctl ABI for libcfs/LNet control operations.

Important APIs/types: `LNET_IOCTL_VERSION` and `LNET_IOCTL_VERSION2` version payload formats. `libcfs_ioctl_hdr` carries length/version. `libcfs_ioctl_data` is the legacy flexible container with NID, u32/u64 arrays, inline buffer lengths/pointers, userspace buffers, and trailing bulk data. Macros define ioctl command numbers for debug, NI queries, fail/discover/ping/fault operations, LND connection/peer/interface commands, and dynamic LNet configuration commands through `IOC_LIBCFS_MAX_NR`.

Control flow: user tools fill a versioned header/container and call ioctls; kernel dispatch uses command numbers and copies inline or userspace bulk buffers.

State and persistence: no persistence. Operations mutate/query kernel LNet state depending on command.

Dependencies/integration: includes Linux ioctl/types and defines `__user` for sparse compatibility. Later DLC structures referenced by command sizes are declared in `lnet-dlc.h`.

Risks and test signals: comments state older ioctl definitions are broken in their `_IOWR` type/size usage, so compatibility must be preserved. Pointer fields make 32/64-bit compatibility and copy bounds important. Test signals are version validation, max data size enforcement, compat ioctls, every command number remaining stable, and safe handling of user pointers/bulk lengths.
