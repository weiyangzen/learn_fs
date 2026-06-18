<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/unaligned.h -->
# sources/distributed-fs/ceph-client/include/vdso/unaligned.h

Purpose: provides vDSO-safe unaligned load/store macros that avoid undefined behavior and strict-aliasing assumptions.

Important APIs and types: `__get_unaligned_t(type, ptr)` copies bytes into an unqualified scalar temporary and returns it. `__put_unaligned_t(type, val, ptr)` copies a scalar temporary to an unaligned pointer.

Control flow: code parsing unaligned data in vDSO-compatible contexts can use these macros instead of type-punning or direct unaligned dereferences.

State and persistence: no state; memory helper macros only.

Dependencies and integration points: depends on compiler type helpers from `linux/compiler_types.h`. It integrates with arch/generic vDSO code needing portable unaligned access.

Risks and test signals: risks include misuse with non-scalar types, volatile/MMIO pointers, and sanitizer interactions. Test unaligned loads/stores under UBSAN/KASAN-compatible builds and strict-aliasing compilers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/unaligned.h -->
