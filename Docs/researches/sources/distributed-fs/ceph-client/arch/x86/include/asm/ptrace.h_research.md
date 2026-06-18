<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/ptrace.h

Purpose: defines the kernel-visible x86 `pt_regs` layouts and register access helpers used by entry code, ptrace, kprobes, ftrace, syscall handling, signal delivery, and stack unwinding. It also models FRED CS/SS extension fields on 64-bit builds.

Important APIs/types/functions: 32-bit and 64-bit `struct pt_regs`, `fred_cs`, `fred_ss`, `regs_return_value()`, `regs_set_return_value()`, `user_mode()`, `v8086_mode()`, `user_64bit_mode()`, `any_64bit_mode()`, `ip_within_syscall_gap()`, register pointer accessors, `regs_get_register()`, stack-range helpers, `regs_get_kernel_stack_nth()`, `regs_get_kernel_argument()`, single/block-step capability macros, and thread-area prototypes.

Control flow: entry assembly populates `pt_regs`; generic kernel code uses the helpers to classify user/kernel origin, retrieve return values, recover function arguments, and walk saved kernel stack slots. FRED-enabled 64-bit systems extend the saved CS/SS slots with event metadata; compat and 32-bit code handle vm86 and 16-bit selector fields specially.

State and persistence: `pt_regs` instances live on kernel stacks or exception frames and are transient, but their layout is ABI-sensitive through ptrace, signal frames, perf, kprobes, and core dumps. Dependencies include segment constants, page/thread sizes, paravirt extra user CS, entry symbols from `proto.h`, and nofault copying.

Risks: any layout or offset drift breaks assembly, debugger ABI, syscall tracing, and signal return. Stack argument recovery is heuristic and must avoid unsafe kernel memory reads. FRED metadata must remain synchronized with hardware event-frame format. Test signals include ptrace register read/write, signal delivery/return, syscall tracing, kprobe/ftrace argument fetches, FRED and non-FRED entry tests, vm86 on 32-bit, and compat syscall paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ptrace.h -->
