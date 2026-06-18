<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/uprobes.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/uprobes.h

Purpose: declares LoongArch uprobes breakpoint instruction, XOL slot handling, and architecture-specific uprobe state.
Important APIs and types: defines `UPROBE_SWBP_INSN`, `UPROBE_SWBP_INSN_SIZE`, `struct arch_uprobe`, and helpers for return probes and single-step/breakpoint handling.
Control flow: uprobes patches user instructions with breakpoints, executes displaced instructions out of line, then redirects control back through arch handlers.
State and persistence: `arch_uprobe` stores copied instruction words and fixup metadata associated with a probed site.
Dependencies and integration: integrates with `kernel/uprobes.c`, LoongArch instruction decoder/generator, break exception handling, ptrace, and perf uprobes.
Risks and test signals: wrong instruction emulation or XOL return handling corrupts user execution. Signals include perf probe/uprobe tests, uprobes selftests, branch instruction probes, and signal interaction tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/uprobes.h -->
