<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ptrace-abi.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ptrace-abi.h

Purpose: Defines x86 ptrace register offsets, frame size constants, and architecture-specific ptrace request numbers.

Important APIs/types/functions: i386 register indices `EBX` through `SS`, x86_64 frame offsets `R15` through `SS`, `FRAME_SIZE`, `PTRACE_GETREGS`, `PTRACE_SETREGS`, `PTRACE_GETFPREGS`, `PTRACE_SETFPREGS`, `PTRACE_GETFPXREGS`, `PTRACE_SETFPXREGS`, `PTRACE_GET_THREAD_AREA`, `PTRACE_SET_THREAD_AREA`, `PTRACE_ARCH_PRCTL`, `PTRACE_SYSEMU`, `PTRACE_SYSEMU_SINGLESTEP`, and `PTRACE_SINGLEBLOCK`.

Control flow: Debuggers call ptrace requests; kernel copies register frames according to these offsets and request numbers. Assembly and frame-offset generation can use the same constants.

State and persistence behavior: No state. Register offsets define the ABI for observing and mutating task register state.

Dependencies and integration points: Integrates with ptrace, syscall tracing, TLS/thread-area manipulation, seccomp/syscall emulation tools, debuggers, CRIU, and kernel entry frame layout.

Risks and test signals: Risks include register offset drift, frame-size mismatch, and compat request handling regressions. Test gdb/strace, ptrace selftests, i386 compat tracing, syscall emulation, thread-area get/set, and generated frame offset comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ptrace-abi.h -->
