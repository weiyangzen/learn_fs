# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/ftrace.h

## Purpose

`ftrace.h` defines LoongArch ftrace and graph tracing hooks. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 91 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: _mcount, prepare_ftrace_return, dyn_arch_ftrace, ftrace_init_nop, ftrace_call_adjust, arch_ftrace_get_regs, ftrace_graph_func. Symbol extraction from the file shows representative defines `_ASM_LOONGARCH_FTRACE_H`, `FTRACE_PLT_IDX`, `FTRACE_REGS_PLT_IDX`, `NR_FTRACE_PLTS`, `MCOUNT_INSN_SIZE`, `mcount`, `ARCH_SUPPORTS_FTRACE_OPS`, `ftrace_init_nop`, `ftrace_regs_get_frame_pointer`, `ftrace_graph_func`, `arch_ftrace_set_direct_caller`, representative callable declarations or inline helpers `_mcount`, `prepare_ftrace_return`, `ftrace_init_nop`, `ftrace_call_adjust`, `prepare_ftrace_return`, `arch_ftrace_get_regs`, `ftrace_graph_func`, and representative local types `dyn_ftrace`, `dyn_arch_ftrace`, `ftrace_ops`. Direct includes seen in the header are `linux/ftrace_regs.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by dynamic ftrace, function graph tracer, kprobes and module text patching. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: instruction patch size, callsite adjustment and pt_regs extraction must match generated prologues. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
