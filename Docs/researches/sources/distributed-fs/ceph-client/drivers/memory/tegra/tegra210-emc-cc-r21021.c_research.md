# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc-cc-r21021.c

## Purpose
This file implements the Tegra210 EMC clock-change sequence revision r21021. It is not a platform driver; it exports `tegra210_emc_r21021`, a `struct tegra210_emc_sequence` with callbacks for DVFS clock changes and periodic clock-tree compensation. The code programs EMC, MC, DRAM mode, calibration, DLL, ZQ, pad, and CCFIFO operations in a strict hardware-defined order.

## Important APIs, Types, And Functions
The exported object is `tegra210_emc_r21021`. The main callback is `tegra210_emc_r21021_set_clock()`. Periodic training uses `tegra210_emc_r21021_periodic_compensation()`, `periodic_compensation_handler()`, `tegra210_emc_get_clktree_delay()`, and `tegra210_emc_compare_update_delay()`. The PTFV macros maintain fixed-point moving averages for DQS oscillator-derived clock-tree delays. The sequence relies on helper APIs from `tegra210-emc-core.c` and `tegra210-emc.h`, including `emc_writel()`, `emc_channel_writel()`, `ccfifo_writel()`, `tegra210_emc_timing_update()`, `tegra210_emc_dll_prelock()`, `tegra210_emc_do_clock_change()`, and power ramp helpers.

## Control Flow
For periodic compensation, the code disables power optimizations, disables DLL, waits for channels to leave powerdown/self-refresh, samples DQSOSC MRR18/MRR19, updates moving averages, optionally writes compensated trim registers, restores EMC config, updates timing, and re-enables DLL. For a DVFS clock change, `set_clock()` computes source/destination periods and DRAM type, disables DLL/autocal/power features, optionally performs clock-tree compensation, prelocks or disables the DLL, prepares autocal, handles LPDDR4/LPDDR3/DDR3 special cases, writes burst/per-channel/vref/trim/MC latency registers, enters self-refresh through CCFIFO, ramps pads down, triggers the clock change, ramps pads up, exits self-refresh, issues MRWs/ZQ/refresh/QRST operations, restores ZCAL/EMC config/FDPD/autocal, and leaves `emc->last` update to the core caller.

## State And Persistence
The sequence mutates `emc->last`, `emc->next`, timing-table fields such as `ptfv_list` and current clock-tree values, a static `fsp_for_next_freq` toggle for LPDDR4 FSP selection, and many EMC/MC hardware registers. Moving averages and compensated clktree values persist in the selected timing structures while the driver is loaded. Hardware mode-register, DLL, pad, ZQ, self-refresh, autocal, and latency-allowance state changes persist until the next rate change or suspend/resume reprogramming.

## Dependencies And Integration Points
It depends on Tegra210 EMC register definitions and timing-table layout in `tegra210-emc.h`, MC register definitions in `tegra210-mc.h`, common core helpers from `tegra210-emc-core.c`, and the Tegra210 clock provider. The core selects this sequence when a reserved-memory timing table has revision `0x7`. The algorithm is tightly coupled to table indices such as `EMC_CFG_INDEX`, `EMC_ZCAL_INTERVAL_INDEX`, `EMC_MRW*`, trim arrays, burst MC arrays, and per-channel register offset tables.

## Risks
This is a high-risk hardware transaction: ordering, delays, and table fields are all critical to DRAM stability. Several loops wait for hardware conditions without timeout in DLL prelock-related helper paths outside this file's direct control. Static `fsp_for_next_freq` is global to the sequence, so multiple controllers would share it, though Tegra210 normally has one EMC instance. Unsupported or malformed timing tables can lead to wrong MRWs, pad ramps, ZQ timing, or trimmer compensation. Removed training sections mean correctness depends on pre-trained table values and periodic compensation.

## Test Signals
Tests must be hardware based: sweep every EMC OPP up and down under memory stress, exercise LPDDR4 and non-LPDDR4 paths where available, verify periodic training timer changes trim values only when margins are exceeded, and monitor for MC/EMC faults, data corruption, DLL lock warnings, and clock-change completion warnings. Thermal refresh transitions and suspend/resume should be tested in combination with DVFS because they select nominal/derated tables and invoke this sequence.
