<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ptrace.h

Purpose: Defines SPARC trap/register-frame, register-window, stack-frame, offset, and ptrace request ABI for 32-bit and 64-bit users.

Important APIs and control flow: 64-bit `pt_regs` stores globals/ins, tstate, tpc, tnpc, y, and a magic/trap-type word; 32-bit `pt_regs` stores psr, pc, npc, y, and globals/ins. The header defines 64-bit and 32-bit register windows and stack frames, trap-frame helpers, register indexes (`UREG_*`), assembler-visible sizes, field offsets, and SPARC-specific ptrace request numbers including 64-bit register operations for mixed-debugger cases.

State, dependencies, and risks: state is trap stack frames, user register sets, register windows, and debugger-visible process state. Dependencies include `psr.h`/`pstate.h`, syscall/trap assembly, signal code, unwinder magic, and ptrace core. Risks are offset drift breaking assembly, wrong struct layout for compat debuggers, and unwinder false positives if magic semantics change. Test signals are ptrace get/set regs/fpregs for 32-bit and 64-bit tasks, signal frame unwinding, register-window spill tests, and syscall tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ptrace.h -->
