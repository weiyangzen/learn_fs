<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/Makefile

Purpose: builds the SH kernel core object set.

Important APIs/types/functions: object lists for head, traps, IRQ, process, ptrace, signal, syscall, time, topology, cache/TLB, SMP, ftrace, DWARF unwind, PCI, PM, kprobes, kgdb, perf, and platform sections.

Control flow: Kbuild selects objects from config symbols and removes `-pg` from ftrace/return-address files when needed.

State and persistence: build state only; no runtime persistence.

Dependencies/integration: integrates the whole SH architecture kernel with config-driven object inclusion and linker script generation.

Risks: wrong object selection causes missing boot entry, trap, or syscall code only for some configs.

Test signals: build representative SH configs including SMP, MMU, ftrace, PCI, PM, and kprobes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/Makefile -->
