<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/uprobes.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/uprobes.h

Purpose: Defines RISC-V uprobes breakpoint instruction properties and arch hooks.

Important APIs/types/functions: Declares `uprobe_opcode_t`, breakpoint opcode constants, `arch_uprobe` fields, and uprobe analysis/emulation entry points.

Control flow: Uprobe code copies/analyzes an instruction, plants a breakpoint, single-steps or emulates, then resumes user execution.

State and persistence: Persistent uprobe state includes original instruction bytes, slot metadata, and per-task probe context held by generic uprobes.

Dependencies and integration points: Integrates with instruction decoding, ptrace, traps, perf uprobes, and user memory access.

Risks: Compressed instruction length and PC-relative emulation mistakes can corrupt user execution.

Test signals: Perf uprobes, uprobes selftests, compressed/non-compressed instruction probes, signal interaction, and multi-threaded probes.

Source read size: 51 lines, 1065 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/uprobes.h -->
