# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/launch.h

Purpose: Shared secondary-CPU launch mailbox layout for MIPS evaluation boards.

Important APIs/types/functions: C code sees `struct cpulaunch` with `pc`, `gp`, `sp`, `a0`, padding to avoid cacheline thrashing, and `flags`. Assembly sees offsets `LAUNCH_PC`, `LAUNCH_GP`, `LAUNCH_SP`, `LAUNCH_A0`, `LAUNCH_FLAGS` and `LOG2CPULAUNCH`. Flag bits are `LAUNCH_FREADY`, `LAUNCH_FGO`, and `LAUNCH_FGONE`. The mailbox base is `CPULAUNCH`, with `NCPULAUNCH` slots and `LAUNCHPERIOD` poll interval.

Control flow, state, and persistence: Boot CPU writes launch parameters and flag transitions; secondary CPUs poll and update flags. State persists in shared memory or firmware-visible launch area.

Dependencies and integration: Used by SMP bring-up assembly and C board code. Its layout must match both C and assembler consumers.

Risks and test signals: Padding, offset, or flag changes can deadlock secondary CPU startup. Test with SMP boot, cache coherency stress during bring-up, and assembly offset checks against `struct cpulaunch`.
