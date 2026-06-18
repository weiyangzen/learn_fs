# sources/distributed-fs/ceph-client/arch/s390/include/asm/ftrace.h

Purpose: This header defines the s390 architecture contract for function tracing, dynamic ftrace patching, ftrace register access, syscall-name matching, and function graph callbacks.

Important APIs/types/functions: `ARCH_SUPPORTS_FTRACE_OPS`, `MCOUNT_INSN_SIZE`, `return_address()`, `ftrace_return_address`, `ftrace_caller`, `ftrace_func`, empty `struct dyn_arch_ftrace`, `ftrace_need_init_nop()`, `ftrace_init_nop()`, ftrace register helpers, optional `arch_ftrace_set_direct_caller()`, `arch_syscall_match_sym_name()`, `ftrace_graph_func()`, and assembler macros `FTRACE_NOP_INSN`, `FTRACE_GEN_MCOUNT_RECORD`, and `FTRACE_GEN_NOP_ASM` are the exposed surface.

Control flow: Compiled function entry code emits a six-byte `brcl 0,0` nop and, unless compiler hotpatch support owns the records, an entry in `__mcount_loc`. Dynamic ftrace later rewrites those nop slots to branch through `ftrace_caller`; callbacks inspect `struct ftrace_regs`, and full `pt_regs` are only returned when `PIF_FTRACE_FULL_REGS` is set.

State and persistence: The header owns no storage except external declarations, but it defines persistent text patch sites and module hotpatch metadata consumed by ftrace. Direct-call tracing stores the direct target in `orig_gpr2` inside the ftrace register frame as an in-band trampoline signal.

Dependencies and integration points: It depends on s390 stack frames, `pt_regs` flags, Linux ftrace register wrappers, modules, dynamic ftrace records, perf sampling register fill, syscall tracing, and kprobes-on-ftrace classification.

Risks and test signals: Instruction size and nop encoding must match the patcher exactly or live text patching can corrupt functions. Tests should include dynamic ftrace enable/disable, graph tracing, direct calls, perf samples from ftrace, module tracing, syscall event matching for `__s390x_` prefixes, and kprobe-on-ftrace sites.
