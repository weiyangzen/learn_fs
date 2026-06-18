# sources/distributed-fs/ceph-client/arch/nios2/mm/uaccess.c

Purpose: implements Nios II raw_copy_from_user and raw_copy_to_user loops with exception-table fixups for
partial user copies.

Important APIs/types/functions: prototypes: `Copyright`; exports: `raw_copy_from_user`, `raw_copy_to_user`.

Control flow: User-copy loops copy bytes/words until completion or a fault; exception-table fixups redirect the
saved PC to return the uncopied byte count instead of oopsing the kernel.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/export.h`, `linux/uaccess.h`. Integration points include generic Linux
MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus
Nios II control-register assembly. This source is part of the Nios II architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
