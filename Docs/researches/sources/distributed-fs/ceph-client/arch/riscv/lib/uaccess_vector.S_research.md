<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/uaccess_vector.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/uaccess_vector.S

## Purpose
`uaccess_vector.S` provides vectorized byte user-copy loops for RISC-V vector-capable MMU kernels.

## Important APIs, Types, And Functions
It exports `__asm_vector_usercopy` and `__asm_vector_usercopy_sum_enabled`. The code uses `vsetvli`, `vle8.v`, and `vse8.v` with exception-table fixups.

## Control Flow
The non-SUM wrapper enables SUM, calls the SUM-enabled loop, then clears SUM. The loop sets vector length for remaining bytes, loads bytes from source, subtracts the vector length, stores to destination, advances pointers, and repeats. Load faults return current remaining bytes; store faults adjust remaining bytes using `CSR_VSTART`.

## State And Persistence
It temporarily mutates SUM and vector state while copying memory. No persistent state is kept.

## Dependencies And Integration Points
It is called from `enter_vector_usercopy()` and relies on vector context guards in C, exception table fixups, and RISC-V vector ISA.

## Risks
Fault accounting on partial vector stores must be exact so scalar fallback resumes at the right byte. SUM cleanup must run after wrapper calls. Vector state must only be used inside kernel vector critical sections.

## Test Signals
Large usercopy tests with page faults at load and store boundaries, vector preemption stress, and comparison with scalar remaining-byte behavior are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/uaccess_vector.S -->
