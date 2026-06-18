<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/vdso/unaligned.h -->
# sources/distributed-fs/ceph-client/tools/include/vdso/unaligned.h

Purpose: this header provides safe unaligned scalar load/store macros for vDSO and low-level code.

Important APIs/types: `__get_unaligned_t(type, ptr)` declares a non-const scalar temporary via `__unqual_scalar_typeof`, copies bytes from `ptr` with `__builtin_memcpy`, and returns the value. `__put_unaligned_t(type, val, ptr)` copies a scalar value into an unaligned destination. Both cast through `void *` to avoid UBSAN noise.

Control flow: macro expansion performs a fixed-size `memcpy` at the call site. No loops or external functions are required.

State and persistence: the get macro reads caller memory; the put macro mutates caller memory. There is no persistent state.

Dependencies/integration: includes `linux/compiler_types.h` for attributes and scalar type helpers. Used when direct unaligned dereference or type punning would violate strict aliasing or alignment rules.

Risks and test signals: risks include passing expressions with side effects, incorrect `type`, invalid pointers, and endian assumptions left to callers. Test under UBSAN/ASAN, strict-aliasing builds, and architectures that fault on unaligned accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/vdso/unaligned.h -->
