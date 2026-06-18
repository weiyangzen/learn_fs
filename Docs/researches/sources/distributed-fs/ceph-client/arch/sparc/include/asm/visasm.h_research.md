<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/visasm.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/visasm.h

Purpose: Provides SPARC64 assembly and inline-C entry/exit helpers for VIS routines that need controlled FPU register ownership.

Important APIs and control flow: `VISEntry` reads `%fprs`, calls `VISenter` if FPU state is dirty/enabled, then enables FPRS_FEF for VIS instructions. `VISExit` clears `%fprs`. The half and fast variants support routines that preserve `%o5` and can branch to a failure label if FPU state is already enabled. `save_and_clear_fpu()` emits equivalent inline assembly for C callers, and `vis_emul()` is declared for VIS instruction emulation from trap code.

State, dependencies, and risks: state is CPU-local FPU register state and `%fprs` dirty bits. Dependencies include `asm/pstate.h`, `asm/ptrace.h`, the external `VISenter` routine, and SPARC register conventions. Risks are clobber-list mismatches, using these macros around code that cannot tolerate `%g*` or `%o5` clobbers, and missing save/restore on paths with early exits. Test signals are VIS crypto/copy routines under preemption, FPU-heavy workloads, and emulation traps that preserve user FPU state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/visasm.h -->
