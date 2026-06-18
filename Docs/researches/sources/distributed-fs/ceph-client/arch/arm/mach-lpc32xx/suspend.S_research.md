# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/suspend.S

Purpose: IRAM-executed LPC32xx low-level suspend routine that places SDRAM into self-refresh, disables HCLK PLL, enters halt, then restores clocks and SDRAM.

Important APIs/types/functions: Defines `lpc32xx_sys_suspend` and `lpc32xx_sys_suspend_sz`.

Control flow: The routine saves registers to a local IRAM stack, loads clock/power and EMC bases, waits for a DRAM busy-to-idle window, requests self-refresh and waits for acknowledge, enters direct-run mode, stops DDR clock, saves/disables HCLK PLL, sets stop mode until wake, restores PLL and waits for lock, restores run mode and DRAM clock, clears self-refresh, waits for EMC exit, restores registers, and returns.

State and persistence: State is saved register values in IRAM plus hardware clock/power, HCLK divider, HCLK PLL, and EMC self-refresh state. No DRAM access is allowed while clocks are unavailable.

Dependencies and integration points: Depends on `pm.c` copying this code to IRAM, `lpc32xx.h` register definitions, and ARM assembler/linkage.

Risks: Polling loops have no timeout. The PLL status wait condition is hardware-specific and any wrong bit interpretation can hang. The routine assumes the IRAM location and local stack are safe and that wake sources are configured before suspend.

Test signals: Suspend/resume on SDRAM and DDR LPC32xx boards, verify wake events, PLL lock, DRAM retention, and no corruption of original IRAM contents.
