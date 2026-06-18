# sources/distributed-fs/ceph-client/arch/sparc/lib/VISsave.S

Purpose: Saves/restores or prepares VIS/FPU state for kernel VIS-using routines.

Important APIs/functions: Exports `VISenter`.

Control flow: `VISenter` inspects floating-point register state in `%fprs` and thread metadata (`TI_FPSAVED`). It saves dirty lower/upper FP register halves into the current thread as needed, updates saved flags, issues synchronization barriers, enables FPRS state, and returns through the caller-supplied `%g7` continuation.

State and persistence: Persists FP/VIS register contents into current thread save areas and updates thread flags.

Dependencies/integration: Includes `asm/ptrace.h`, `asm/visasm.h`, `asm/thread_info.h`, `asm/page.h`, and ASI definitions. Used by assembly memory routines that rely on VIS.

Risks/test signals: Incorrect save/restore corrupts user FP state. Test context switches around VIS-using kernel paths, signal delivery with FP state, and stress copy/memset routines under FP-heavy workloads.
