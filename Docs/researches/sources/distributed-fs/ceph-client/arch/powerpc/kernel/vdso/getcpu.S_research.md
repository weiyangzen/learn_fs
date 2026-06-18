# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/getcpu.S

## Purpose
Implements the vDSO `__kernel_getcpu` fast path for PowerPC, returning CPU and NUMA node without a syscall where supported.

## Important APIs, Types, And Functions
Exports `__kernel_getcpu(unsigned *cpu, unsigned *node)`. On 64-bit it reads `SPRN_SPRG_VDSO_READ`; on non-SMP builds it returns zero for both CPU and node.

## Control Flow
The 64-bit path reads a packed SPRG value where low 16 bits are CPU and the next 16 bits are node, stores each value only if the caller pointer is non-null, clears SO, and returns zero. The non-SMP fallback stores zeroes similarly.

## State And Persistence
Reads per-CPU SPRG state initialized by `vdso_getcpu_init` and maintained in PACA. It does not mutate state.

## Dependencies And Integration Points
Depends on `vdso.c` setting `SPRN_SPRG_VDSO_WRITE`, CPU-to-node topology, and linker scripts exporting `__kernel_getcpu` only for 64-bit or non-SMP 32-bit cases.

## Risks And Edge Cases
CPU and node values are truncated to 16 bits. The function is absent for SMP 32-bit, so userspace must handle symbol availability or fallback.

## Test Signals
Userspace `getcpu` tests should compare vDSO results with syscall results across CPUs and NUMA nodes, including null pointer arguments and task migration.
