# sources/distributed-fs/ceph-client/tools/arch/alpha/include/uapi/asm/mman.h

## Purpose
Defines Alpha memory mapping, protection, and madvise constants for tools, including fallback constants missing on Alpha.

## Important APIs, Types, And Functions
- Defines `MADV_*`, `MAP_*`, and `PROT_*` constants with Alpha ABI values.
- Provides tool compatibility fallbacks for `MADV_HWPOISON`, `MADV_SOFT_OFFLINE`, `MAP_32BIT`, and `MAP_UNINITIALIZED`.

## Control Flow
No runtime flow.

## State And Persistence
No state. Constants affect compiled tools ABI.

## Dependencies And Integration Points
Used by tools such as perf that need mman constants across architectures.

## Risks
Wrong values can break mmap/madvise decoding or invocation in tools. Fallback constants set unsupported features to harmless or conventional values for build compatibility.

## Test Signals
Cross-compile perf/tools for Alpha and compare generated constants against Alpha UAPI.
