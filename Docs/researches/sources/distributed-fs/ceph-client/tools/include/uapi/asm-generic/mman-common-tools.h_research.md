# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/mman-common-tools.h

## Purpose
Restores common mmap type flags for tools builds whose local UAPI include path shadows system headers after those flags moved to `linux/mman.h`.

## Important APIs, Types, and Functions
Includes `asm-generic/mman-common.h` and conditionally defines `MAP_SHARED`, `MAP_PRIVATE`, and `MAP_SHARED_VALIDATE` if `MAP_SHARED` is absent.

## Control Flow, State, and Persistence
Preprocessor-only compatibility behavior. No runtime state.

## Dependencies and Integration
Depends on the generic mmap common header and is included by per-architecture `mman.h` wrappers in the tools tree. It integrates with perf and related tools that include both system `sys/mman.h` and tools UAPI headers.

## Risks and Test Signals
Risks include masking inconsistencies with newer system headers and incomplete recovery if only one of the three macros is missing. Test signals are builds with tools UAPI first in the include path and compile checks using `MAP_SHARED`, `MAP_PRIVATE`, and `MAP_SHARED_VALIDATE`.
