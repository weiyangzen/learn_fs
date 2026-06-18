<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sigcontext.h

Purpose: defines the user-visible Xtensa signal context saved in signal frames. Fields include `sc_pc`, `sc_ps`, loop registers, `sc_sar`, accumulator low/high placeholders, 16 address registers, and `sc_xtregs` pointer.

Control flow is used by signal delivery and `rt_sigreturn` to save and restore user execution state. Persistent state is the signal frame placed on the user stack. Dependencies include signal frame code, Xtensa register ABI, and optional Xtensa extension register storage. Integration points are libc signal handlers, debuggers inspecting signal frames, ptrace, and core dumps. Risks are ABI layout changes, incomplete register preservation for extended/TIE state, and invalid user-stack pointers. Test signals include signal handler/return tests, altstack, nested signals, gdb signal frame unwinding, and ABI size/offset checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sigcontext.h -->
