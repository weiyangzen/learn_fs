<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/uprobes.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/uprobes.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/uprobes.h` declares arm64 uprobes architecture state, breakpoint instruction constants, XOL slot sizing, and the single-step handler entry point. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_ASM_UPROBES_H`, `UPROBE_SWBP_INSN`, `UPROBE_SWBP_INSN_SIZE`, `UPROBE_XOL_SLOT_BYTES`; types: `arch_uprobe_task`, `arch_uprobe`, `arch_probe_insn`, `pt_regs`; functions/prototypes/exports: `uprobe_single_step_handler`. The file is 42 lines / 868 bytes. Direct includes are `asm/debug-monitors.h`, `asm/insn.h`, `asm/probes.h`.

### Control Flow
The generic uprobes core stores decoded arm64 probe instruction data in `struct arch_uprobe`, replaces probed userspace instructions with `UPROBE_SWBP_INSN`, executes the copied instruction from an XOL slot, then routes single-step completion through `uprobe_single_step_handler`.

### State, Persistence, And Dependencies
Notable global/static state symbols are `api`, `simulate`, `uprobe_brk_handler`, `uprobe_single_step_handler`. `arch_uprobe_task` tracks per-task probe execution state and `arch_uprobe` stores decoded probe metadata. State lives in uprobe/task structures, not persistent storage. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong instruction decode, breakpoint size, or XOL slot assumptions can corrupt userspace state, mis-handle PC-relative instructions, or leave threads stuck after single-step.

### Test Signals
Run uprobes/perf tests for A64 and compat tasks, test PC-relative and faulting instructions, and verify breakpoint restore across signal and exec paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/uprobes.h -->
