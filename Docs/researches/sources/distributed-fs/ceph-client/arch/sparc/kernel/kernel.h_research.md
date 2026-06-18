# sources/distributed-fs/ceph-client/arch/sparc/kernel/kernel.h

## Purpose
`kernel.h` is a local SPARC kernel-private declaration hub. It connects architecture assembly and C files without exporting all declarations through global UAPI-style headers.

## Important APIs, Types, and Functions
It declares process creation helpers (`sparc_clone`, `sparc_fork`, `sparc_vfork`, `sparc_clone3`), sparc64 setup/syscall/trap/SMP/compat helpers, sparc32 setup/trap/IRQ/SMP/signal/ptrace/window helpers, and platform externs. The sparc64 inline `kimage_addr_to_ra()` converts a kernel virtual address to real address using `kern_base` and `KERNBASE`.

## Control Flow and State
There is no implementation. It fixes architecture-local linkage between files such as `entry.S`, `ds.c`, IRQ code, trap handlers, signal code, and setup code.

## Persistence and Dependencies
The header declares persistent state such as `sparc_pmu_type`, `fsr_storage`, `ncpus_probed`, boot/trap symbols, PCIC registers, and platform vectors. Dependencies include trap, head, IO, ftrace, and interrupt headers.

## Integration Points, Risks, and Test Signals
Integration is broad across sparc32 and sparc64 architecture code. Risks include stale declarations after function signature changes, config-guard mismatches, and misuse of `kimage_addr_to_ra()` before `kern_base` is valid. Test signals are clean sparc32/sparc64 builds across configs and boot paths that exercise declared assembly/C interfaces.
