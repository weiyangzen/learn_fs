<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kprobes.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kprobes.h

## Purpose
Declares RISC-V kprobe instruction-slot, breakpoint, single-step, and fault handling hooks.

## Important APIs, Types, And Functions
types `prev_kprobe`, `kprobe`, `kprobe_ctlblk`, `pt_regs`; functions/prototypes `arch_remove_kprobe`, `kprobe_fault_handler`, `kprobe_breakpoint_handler`, `kprobe_single_step_handler`; macros/constants `_ASM_RISCV_KPROBES_H`, `__ARCH_WANT_KPROBES_INSN_SLOT`, `MAX_INSN_SIZE`, `flush_insn_slot(p) do { } while (0)`, `kretprobe_blacklist_size`.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
Direct includes are `asm-generic/kprobes.h`, `linux/types.h`, `linux/ptrace.h`, `linux/percpu.h`, `asm/probes.h`. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 54 lines, 1216 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kprobes.h -->
