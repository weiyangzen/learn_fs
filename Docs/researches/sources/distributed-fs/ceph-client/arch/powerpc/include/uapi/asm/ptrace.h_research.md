<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ptrace.h

Purpose: Defines PowerPC ptrace register frame layout, offsets, ptrace request numbers, and hardware breakpoint ABI.

Important APIs/types/functions: `struct pt_regs`/`user_pt_regs`, `PT_*` offsets, FP/VMX/VSX register offsets, ptrace requests for VR/EVR/VSR, syscall emulation and 32-on-64 access, `struct ppc_debug_info`, `struct ppc_hw_breakpoint`, and breakpoint feature/mode/condition flags.

Control flow: Kernel entry saves volatile registers in this layout; ptrace and core code use offsets to copy registers; debuggers issue requests to get/set register sets or configure hardware breakpoints/watchpoints.

State and persistence: Represents per-thread register and debug state visible to tracers and core dumps.

Dependencies and integration points: Depends on Linux types and architecture trap/ptrace/debug register code. Integrated by GDB, strace, perf, and signal/core paths.

Risks: Offsets are binary ABI and correspond to kernel stack layouts. Hardware breakpoint flags must match DAWR/IABR/DABR capabilities and alignment limits.

Test signals: ptrace register get/set tests, GDB single-step/syscall emulation, hardware breakpoint/watchpoint tests, core dump validation, and compat 32/64 tracing tests.

Source read size: 272 lines, 7793 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ptrace.h -->
