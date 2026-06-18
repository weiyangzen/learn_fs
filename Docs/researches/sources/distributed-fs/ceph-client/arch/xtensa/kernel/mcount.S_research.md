<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/mcount.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/mcount.S

Purpose: provides Xtensa ftrace `_mcount` and `ftrace_stub`. It checks `ftrace_trace_function`, returns if it points to the stub, otherwise computes caller and parent IPs and calls the active tracer.

Control flow differs by ABI. Windowed ABI uses `abi_entry_default`, reconstructs IPs from return-address encodings relative to stack pointer, subtracts `MCOUNT_INSN_SIZE`, and calls through `callx4`. Call0 ABI preserves caller argument and callee-saved registers on a local frame, passes adjusted caller IP, calls the tracer with `callx0`, then restores registers. Persistent state is none except ftrace global function pointer and caller stack/register state. Dependencies include `asm/asmmacro.h`, `asm/ftrace.h`, ABI macros, and ftrace core. Integration points are function tracer, dynamic tracing, profiling, and module instrumentation. Risks are register clobbering, wrong callsite IP reconstruction, ABI-specific frame size mistakes, and recursion if stub checks fail. Test signals include function graph/function tracer enablement, both ABI builds, module tracing, and tracer stress under interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/mcount.S -->
