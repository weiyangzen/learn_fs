# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pm.c

Purpose: implements Davinci suspend-to-RAM setup and entry using SRAM-resident assembly.

Important APIs/types/functions: `davinci_sram_suspend`, `pm_config`, `davinci_sram_push()`, `davinci_pm_suspend()`, `davinci_pm_enter()`, `davinci_pm_ops`, and `davinci_pm_init()`.

Control flow: init allocates SRAM, copies `davinci_cpu_suspend`, fills `davinci_pm_config` with DDR/PLL/deepsleep addresses, and registers suspend ops. Enter validates `PM_SUSPEND_MEM`, saves interrupt state, calls the SRAM suspend function, and restores state.

State and persistence: SRAM copy of suspend code and `pm_config` persist after init. Hardware state includes PLL, DDR2, and deepsleep registers manipulated during suspend.

Dependencies and integration: depends on `sram_alloc()`, `da8xx_get_mem_ctlr()`, assembly symbols from `sleep.S`, clock/PLL constants, and Linux suspend core.

Risks: failures to allocate SRAM or map DDR controller disable suspend. Assembly must run from SRAM while DDR/PLL state changes. Incorrect deepsleep count or PLL addresses can hang resume.

Test signals: suspend registration logs, SRAM allocation success, DA850 mem suspend/resume loops, and register tracing around DDR self-refresh.
