# sources/distributed-fs/ceph-client/include/uapi/asm-generic/mman.h

Purpose: Adds generic architecture mmap and mlock constants on top of `mman-common.h`.

Important APIs/types/functions: Defines `MAP_GROWSDOWN`, `MAP_DENYWRITE`, `MAP_EXECUTABLE`, `MAP_LOCKED`, `MAP_NORESERVE`, `MCL_CURRENT`, `MCL_FUTURE`, `MCL_ONFAULT`, and shadow-stack setup flags.

Control flow: Header includes common definitions, then adds generic flags while reserving bits 26-31 for hugetlb encoding.

State/persistence: No runtime state; constants are memory-management syscall ABI.

Dependencies/integration: Used by libc and kernel UAPI for `mmap`, `mlockall`, and shadow-stack setup interfaces.

Risks: Flag collisions with architecture-specific flags or hugetlb bits are ABI-breaking.

Test signals: Headers compile checks and mmap/mlock/shadow-stack flag validation where supported.
