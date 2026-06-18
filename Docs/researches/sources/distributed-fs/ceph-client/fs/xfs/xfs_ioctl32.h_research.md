## sources/distributed-fs/ceph-client/fs/xfs/xfs_ioctl32.h

Purpose: defines the 32-bit compat XFS ioctl structures and ioctl numbers whose layout differs from native kernel structures.

Important APIs and types: key types include `compat_xfs_bstime_t`, packed `struct compat_xfs_bstat`, `struct compat_xfs_fsop_bulkreq`, `compat_xfs_fsop_handlereq_t`, packed `struct compat_xfs_swapext`, compat attrlist and attrmulti handle request structs, and x86-specific packed geometry/growfs/inogrp structs. It defines compat ioctl numbers such as `XFS_IOC_FSBULKSTAT_32`, `XFS_IOC_FSINUMBERS_32`, handle ioctls, `XFS_IOC_SWAPEXT_32`, and x86 alignment variants.

Control flow: no executable flow exists here; `xfs_ioctl32.c` switches on these constants and copies these layouts to native structs before delegation.

State and persistence behavior: the header stores no state. Its definitions control how compat userspace describes persistent operations such as growfs, swapext, handle open/readlink, and attr mutation.

Dependencies and integration: integrates with Linux compat pointer and time types. `BROKEN_X86_ALIGNMENT` is selected on `CONFIG_X86_64`, forcing packed structures for historical x86 ABI compatibility. The structure definitions must remain synchronized with old userspace expectations and with native conversion code.

Risks and test signals: padding, packing, pointer width, and 32-bit time truncation are the main risks. Build tests should cover `CONFIG_COMPAT`, `CONFIG_X86_64`, and x32. Runtime tests should compare native and 32-bit ioctl outputs for bulkstat/inumbers and validate swapext/handle/attr operations from a 32-bit test binary.
