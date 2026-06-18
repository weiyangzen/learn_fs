<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/string.h

## Purpose
Advertises OpenRISC architecture implementations of `memset()` and `memcpy()` to generic kernel string code.

## Important APIs, Types, And Functions
Defines `__HAVE_ARCH_MEMSET` and `__HAVE_ARCH_MEMCPY`, then declares `memset(void *s, int c, __kernel_size_t n)` and `memcpy(void *dest, const void *src, __kernel_size_t n)`.

## Control Flow
No flow in the header. Build selection routes calls to `arch/openrisc/lib/memset.S` and `memcpy.c`.

## State And Persistence
No persistent state. The functions mutate caller-provided memory.

## Dependencies And Integration Points
Requires kernel type definitions for `__kernel_size_t`. Integrated by generic string headers and module exports.

## Risks
Prototype mismatch would break builtins, modules, or sanitizer expectations. The implementations do not provide overlap semantics for `memcpy`.

## Test Signals
Kernel string selftests, boot-time memory initialization, and module references to exported `memset`/`memcpy`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/string.h -->
