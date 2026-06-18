<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unaligned/packed_struct.h -->
# sources/distributed-fs/ceph-client/include/linux/unaligned/packed_struct.h

Purpose: implements the generic CPU-endian unaligned access primitives using packed wrapper structs.

Important APIs and types: packed structs `__una_u16`, `__una_u32`, and `__una_u64` wrap 16/32/64-bit values. Helpers `__get_unaligned_cpu16/32/64()` and `__put_unaligned_cpu16/32/64()` perform direct loads/stores through packed pointers.

Control flow: higher-level unaligned macros cast an arbitrary address to a packed wrapper pointer, then load or store the wrapped field so the compiler emits safe unaligned access code for the target architecture.

State and persistence: no independent state exists. Stores modify caller-provided memory.

Dependencies and integration points: depends on `linux/types.h` and compiler support for `__packed`. It backs `linux/unaligned.h` and any architecture-generic unaligned access path.

Risks and test signals: risks include compiler behavior around packed accesses, insufficient buffer length, and accidental use for types larger than the wrappers. Test on strict-alignment architectures and with compiler warning/sanitizer coverage around packed pointer access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unaligned/packed_struct.h -->
