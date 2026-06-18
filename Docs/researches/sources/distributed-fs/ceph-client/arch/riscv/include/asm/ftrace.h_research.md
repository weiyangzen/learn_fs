<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/ftrace.h

## Purpose
Defines RISC-V dynamic ftrace instruction encoding, call patching metadata, ftrace register accessors, and syscall tracing filters.

## Important APIs, Types, And Functions
types `pt_regs`, `dyn_arch_ftrace`, `dyn_ftrace`, `module`, `ftrace_ops`, `ftrace_regs`, `__arch_ftrace_regs`; functions/prototypes `return_address`, `_mcount`, `ftrace_call_adjust`, `arch_ftrace_get_symaddr`, `arch_trace_is_compat_syscall`, `arch_syscall_match_sym_name`, `ftrace_init_nop`, `ftrace_regs_get_instruction_pointer`, `ftrace_regs_set_instruction_pointer`, `ftrace_regs_get_stack_pointer`, `ftrace_regs_get_frame_pointer`, `ftrace_regs_get_argument`, plus 8 more; macros/constants `_ASM_RISCV_FTRACE_H`, `HAVE_FUNCTION_GRAPH_FP_TEST`, `ARCH_SUPPORTS_FTRACE_OPS`, `ftrace_return_address(n) return_address(n)`, `ftrace_get_symaddr(fentry_ip) arch_ftrace_get_symaddr(fentry_ip)`, `ARCH_TRACE_IGNORE_COMPAT_SYSCALLS`, `ARCH_HAS_SYSCALL_MATCH_SYM_NAME`, `MCOUNT_ADDR`, `JALR_SIGN_MASK`, `JALR_OFFSET_MASK`, `AUIPC_OFFSET_MASK`, `AUIPC_PAD`, `JALR_SHIFT`, `JALR_T0`, plus 14 more.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Special attention: call-site rewriting depends on exact AUIPC/JALR encodings, call range checks, NOP sizing, and register accessors for full and partial ftrace frames.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
It has no direct includes. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 242 lines, 6523 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/ftrace.h -->
