# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-system.c

Purpose: provider for AT91 system clocks controlled by SCER/SCDR/SCSR bits, including programmable clock outputs and fixed system gates such as DDR, USB host/device, LCD, and ISI clocks.

Important APIs and data: `at91_clk_register_system()` creates `struct clk_system` with id, regmap, and PM status. Ops implement prepare/unprepare/is_prepared and save/restore. `is_pck()` identifies IDs 8-15, which need readiness polling.

Control flow: prepare writes `SCER` bit; for PCK IDs it waits until the corresponding status bit is ready. unprepare writes `SCDR`. is_prepared checks `SCSR`, then for PCK IDs also checks `PMC_SR`.

State and persistence: save records whether the system clock was prepared and restore re-prepares only previously active clocks. The hardware enable bits persist in PMC system-clock registers.

Dependencies and integration: SoC setup files register system clocks from static tables and pass critical flags for DDR where needed. It depends on parent clocks already being registered and can propagate rate setting to parents via `CLK_SET_RATE_PARENT`.

Risks: PCK readiness wait is unbounded; IDs above 31 are rejected; non-PCK clocks do not verify readiness beyond SCSR. Test signals include SCER/SCSR bit toggles, PCK ready bits, critical DDR clocks not being disabled, and resume restoring prepared system clocks.
