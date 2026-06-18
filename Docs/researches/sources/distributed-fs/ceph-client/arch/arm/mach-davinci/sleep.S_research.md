# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/sleep.S

Purpose: provides SRAM-executed Davinci CPU suspend and DDR PSC configuration assembly.

Important APIs/types/functions: exports `davinci_cpu_suspend`, `davinci_ddr_psc_config`, and `davinci_cpu_suspend_sz`; uses fields from `struct davinci_pm_config`.

Control flow: saves registers, programs DDR/PLL/deepsleep state, waits through fixed timing cycles, enters low-power state, and restores enough state for C resume. The DDR PSC helper manipulates power/sleep control sequences for memory.

State and persistence: executes from SRAM because DDR is placed into low-power/self-refresh state. It temporarily changes PLL, DDR2, and deepsleep controller registers.

Dependencies and integration: paired with `pm.c` copy/setup and `pm.h` structure layout; uses constants from Davinci clock and DDR definitions.

Risks: assembly timing loops depend on expected clock frequency and constants. Wrong struct layout or SRAM copy size can corrupt execution during suspend.

Test signals: link symbol size matches copied code, suspend/resume cycles, and DDR contents validation after resume.
