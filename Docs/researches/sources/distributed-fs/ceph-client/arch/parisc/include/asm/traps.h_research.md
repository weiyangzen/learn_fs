<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/traps.h

Source read size: 24 lines, 667 bytes.

Purpose: declares PA-RISC trap and fault handling entry points shared between assembly, traps, and MM fault code. Important APIs: `PARISC_ITLB_TRAP`, `parisc_terminate()`, `die_if_kernel()`, `parisc_acctyp()`, `trap_name()`, `do_page_fault()`, and `handle_nadtlb_fault()`. Control flow: `entry.S` passes interruption codes into C handlers which use these prototypes to terminate, decode access type, or service page faults. State and persistence: no stored state, but handlers consume and mutate `pt_regs` and task signal/fault state. Dependencies and integration points: integrates with `kernel/traps.c`, `mm/fault.c`, `entry.S`, and ptrace-visible register state. Risks: the ITLB trap code is architecturally fixed; changing prototypes or codes breaks assembly-to-C exception dispatch. Test signals: illegal instruction, page fault, protection fault, non-access TLB fault, kernel oops, and signal-delivery tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/traps.h -->
