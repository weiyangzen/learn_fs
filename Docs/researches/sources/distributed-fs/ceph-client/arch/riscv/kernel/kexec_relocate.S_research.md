# sources/distributed-fs/ceph-client/arch/riscv/kernel/kexec_relocate.S

Purpose: Provides low-level relocation and final jump code for RISC-V kexec.

Important APIs/types/functions: Defines `riscv_kexec_relocate`, `riscv_kexec_norelocate`, and `riscv_kexec_relocate_size`.

Control flow: The relocation path runs from a safe copied buffer, processes kexec indirection pages, copies source pages to destination pages, handles destination/source/control/page flags, flushes caches/TLBs as needed, passes hart ID and FDT pointer, and jumps to the new kernel entry. The no-relocate path disables translation/state and jumps directly when relocation is unnecessary.

State and persistence: Consumes kexec control pages and mutates physical memory into the next kernel layout. It changes SATP/status/interrupt state before transfer.

Dependencies and integration points: Called by `machine_kexec.c`, depends on RISC-V page size, CSR macros, kexec page flags, and boot protocol register conventions.

Risks and test signals: This code executes while replacing the running kernel, so address translation, cache ordering, and flag decoding are high risk. Test normal kexec, crash kexec, large memory maps, relocation across overlapping ranges, and SMP shutdown before jump.
