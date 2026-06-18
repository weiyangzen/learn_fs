# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/mman.h

## Purpose
Adds generic architecture mmap and mlock constants on top of common mmap definitions.

## Important APIs, Types, and Functions
Includes `asm-generic/mman-common-tools.h` and defines `MAP_GROWSDOWN`, `MAP_DENYWRITE`, `MAP_EXECUTABLE`, `MAP_LOCKED`, `MAP_NORESERVE`, `MCL_CURRENT`, `MCL_FUTURE`, `MCL_ONFAULT`, and shadow-stack setup flags `SHADOW_STACK_SET_TOKEN` and `SHADOW_STACK_SET_MARKER`.

## Control Flow, State, and Persistence
Pure macro constants. No state or runtime behavior exists.

## Dependencies and Integration
Depends on the tools mmap-common wrapper. It integrates with syscall wrappers and tools that compile against generic architecture memory-management flags.

## Risks and Test Signals
Risks include architecture-specific deviations, collision with hugetlb-encoded bits in the reserved high range, and consumers assuming shadow-stack flags are supported by all kernels. Test signals are compile checks and targeted `mmap()`/`mlockall()`/shadow-stack syscall probes where supported.
