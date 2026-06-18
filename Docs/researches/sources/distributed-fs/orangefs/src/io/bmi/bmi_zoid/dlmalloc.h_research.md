# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/dlmalloc.h

## Purpose

`dlmalloc.h` is the public declaration header for Doug Lea malloc 2.8.x. It documents compile-time configuration, declares the optional global allocation APIs, declares the `mspace` APIs when `MSPACES` is enabled, and defines mallinfo/tuning symbols when system headers do not provide them. In this directory the header is not included by `zbmi_pool.c` because that file directly includes `dlmalloc.c`; it remains the formal API contract for consumers that compile dlmalloc as a normal component.

## Important APIs, types, and functions

- Configuration macros include `ONLY_MSPACES`, `NO_MALLINFO`, `USE_DL_PREFIX`, `HAVE_USR_INCLUDE_MALLOC_H`, and `MSPACES`.
- Name remapping macros map `dlmalloc` names to standard libc names when `USE_DL_PREFIX` is not defined and `ONLY_MSPACES` is false.
- `struct mallinfo` is declared with `MALLINFO_FIELD_TYPE` fields when no compatible system declaration is being used.
- Global allocator declarations cover `dlmalloc`, `dlfree`, `dlcalloc`, `dlrealloc`, `dlmemalign`, `dlvalloc`, `dlpvalloc`, `dlmallopt`, `dlmalloc_trim`, `dlmalloc_stats`, `dlmalloc_footprint`, `dlmalloc_usable_size`, `dlindependent_calloc`, and `dlindependent_comalloc`.
- `M_TRIM_THRESHOLD`, `M_GRANULARITY`, and `M_MMAP_THRESHOLD` define nonstandard `mallopt` tuning parameter numbers.
- `typedef void* mspace` and the mspace declarations expose independent allocator arenas: creation/destruction, allocation/free/realloc/calloc, memalign, batched allocation helpers, footprint/statistics, trimming, mallinfo, usable size, and mallopt.

## Control flow

The header has no runtime control flow, but its preprocessor branches decide which symbols a translation unit expects. If `ONLY_MSPACES` is true, the global malloc-like declarations are skipped. If `MSPACES` is true, independent arena declarations are emitted. If `NO_MALLINFO` is false, mallinfo-compatible types and functions are exposed.

## State and persistence behavior

The header declares interfaces to allocator-managed process memory but owns no state. The important state contract is that `mspace` is opaque to callers, and all pointers allocated from an mspace must normally be returned through the corresponding mspace API unless the allocator is compiled with footer dispatch support. In the OrangeFS embedding, `FOOTERS` is not set and `zbmi_pool` maintains the single `mspace` handle.

## Dependencies and integration points

The only direct include is `<stddef.h>` for `size_t`. For OrangeFS, the declarations align with the implementation embedded in `zbmi_pool.c`, but `zbmi_pool.c` comments out `#include "dlmalloc.h"` and includes `dlmalloc.c` directly after local compile-time definitions. External users that include this header must compile the allocator implementation with matching macro settings or the declarations will not match linked symbols.

## Risks and edge cases

- The header is generic upstream dlmalloc API material, while this directory's actual build path specializes the implementation through `zbmi_pool.c`. A maintainer can easily infer that `dlmalloc.c` is built separately from this header, but `module.mk.in` does not do that.
- If `USE_DL_PREFIX` is not defined and global APIs are enabled, the header maps `dlmalloc` names to standard allocator names, which can collide with libc declarations.
- `struct mallinfo` compatibility depends on system header choices and `MALLINFO_FIELD_TYPE`; mismatches can cause ABI problems.
- `mspace` is `void *`, so type safety is weak. Passing a destroyed or unrelated mspace is only detected by runtime magic checks in the implementation.

## Test signals

Compile-time tests should check the header under the same macro combinations used by `zbmi_pool.c`: `ONLY_MSPACES=1`, `MSPACES=1`, and the desired alignment/locking settings. A small mspace harness can include the header, link a matching dlmalloc build, create an mspace with a fixed buffer, allocate/free, and verify that no global malloc symbols are required when `ONLY_MSPACES` is set.
