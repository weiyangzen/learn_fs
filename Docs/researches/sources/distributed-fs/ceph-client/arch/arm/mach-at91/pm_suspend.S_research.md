# sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm_suspend.S

Purpose: provides the AT91 final suspend routine that runs from SRAM while clocks and DRAM are being reconfigured or powered down.

Important APIs/types/functions: exports `at91_pm_suspend_in_sram` and `at91_pm_suspend_in_sram_sz`. The assembly uses generated `PM_DATA_*` offsets, RAM controller constants, PMC fields, and conditionals for CPU v7, SAMA7, SAM9X60 PLL support, and legacy SAM v4/v5 controllers.

Control flow: the routine saves caller context, reads the selected mode and controller addresses from `struct at91_pm_data`, places SDRAM/DDR/UDDRC into the correct low-power state, switches master clocks toward slow-clock or low-power PLL configuration, performs WFI or backup shutdown sequencing, and restores clocks and memory-controller state before returning to C.

State and persistence: executes from SRAM because normal RAM may be unavailable. It preserves enough CPU/register state to resume, and relies on C code to preserve backup canary and DDR calibration data. Hardware state includes PMC, PLL, RAMC, DDR PHY, SFRBU, and SHDWC registers.

Dependencies and integration: tightly coupled to `pm.c` setup, `pm.h` layout, `pm_data-offsets.c` generated constants, ARM cache/outer-cache handling, and SoC Kconfig symbols that include or omit code paths.

Risks: this is timing- and ordering-sensitive assembly touching live clock and DRAM control registers. A wrong offset, missing cache flush, unsupported mode, or SoC conditional mismatch can hang the CPU before console output is available. SAMA7 and SAM9X60 PLL branches add extra integration risk because they depend on SoC-specific PMC semantics.

Test signals: link-time symbol size generation, suspend/resume loop tests in each PM mode, SRAM allocation/copy verification, stress with interrupts as wake sources, and failure-injection by omitting DT resources to ensure C code does not enter unsupported assembly paths.
