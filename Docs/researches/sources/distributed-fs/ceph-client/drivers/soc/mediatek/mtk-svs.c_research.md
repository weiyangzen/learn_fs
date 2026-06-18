# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-svs.c

## Purpose
MediaTek Smart Voltage Scaling (SVS) platform driver. It calibrates per-domain operating voltages from efuse data, SVS hardware measurements, OPP tables, regulators, clocks, resets, thermal zones, and PM runtime dependencies. The driver supports MT8183, MT8186, MT8188, MT8192, and MT8195 through static `svs_platform_data` and `svs_bank` tables.

## Important APIs, Types, And Functions
Core types are `struct svs_platform`, `struct svs_platform_data`, `struct svs_bank_pdata`, `struct svs_bank`, `enum svsb_phase`, `enum svsb_sw_id`, `enum svsb_type`, and `enum svs_reg_index`. Register access is wrapped by `svs_readl_relaxed()`, `svs_writel_relaxed()`, and `svs_switch_bank()`. OPP voltage conversion uses `svs_bank_volt_to_opp_volt()` and `svs_opp_volt_to_bank_volt()`. Voltage calculation is split between v2 helpers (`svs_get_bank_volts_v2()`, `svs_set_bank_freq_pct_v2()`) and v3 two-line helpers (`svs_get_bank_volts_v3()`, `svs_set_bank_freq_pct_v3()`).

Main runtime entry points are `svs_probe()`, `svs_start()`, `svs_init01()`, `svs_init02()`, `svs_mon_mode()`, `svs_isr()`, `svs_suspend()`, and `svs_resume()`. Efuse handling flows through `svs_get_efuse_data()`, `svs_get_fuse_val()`, `svs_common_parse_efuse()`, and the MT8183-specific `svs_mt8183_efuse_parsing()`. Debugfs support, when enabled, exposes `dump`, per-bank `enable`, and per-bank `status` views.

## Control Flow
`svs_probe()` selects platform data from OF match data, runs the SoC-specific probe to resolve reset controls, thermal-sensor links, CPU/CCI/GPU OPP devices, reads SVS and thermal calibration nvmem cells, parses efuses, initializes bank resources and OPP tables, maps registers, requests the IRQ, then starts SVS.

Startup runs phases in order. `svs_init01()` pauses cpuidle, enables buck regulators, optionally powers domains through PM runtime, constrains OPPs around the vboot voltage, programs bank registers for INIT01, waits on an IRQ completion, then restores OPP availability, regulators, and PM runtime state. `svs_init02()` programs each eligible bank for INIT02, waits for completion, then synchronizes two-line high/low bank voltage tables from current OPP state. `svs_mon_mode()` enables monitor mode for eligible banks so later thermal-sensitive interrupts can update OPP voltages.

`svs_isr()` scans banks to identify the interrupting bank, selects the hardware bank under `svs_lock`, dispatches to INIT01, INIT02, MON, or error handlers, then calls `svs_adjust_pm_opp_volts()`. The voltage adjustment path locks the bank mutex, chooses the OPP range for one-line or two-line banks, applies thermal offsets when thermal zones are valid, clamps against bank `vmin` and default OPP voltage, and calls `dev_pm_opp_adjust_voltage()`.

Suspend disables all banks, restores default voltages, asserts reset, and disables the main clock. Resume enables the main clock, deasserts reset, repeats INIT02, and re-enters monitor mode.

## State And Persistence
Persistent state is hardware and firmware backed: efuse arrays from nvmem, thermal efuse values, register programming, OPP voltage tables, regulator state, reset/clock state, thermal-zone readings, and PM runtime power state. In-memory state lives in static SoC bank tables copied by reference into the platform object and mutable per-bank fields such as `phase`, `volt[]`, `freq_pct[]`, `opp_dfreq[]`, `opp_dvolt[]`, `dc_voffset_in`, `age_voffset_in`, `temp`, and saved `reg_data`. There is no filesystem persistence; debugfs only reports or disables active banks.

## Dependencies And Integration Points
The driver integrates with platform bus, OF match data, nvmem, OPP, regulator, thermal, reset, clock, PM runtime, CPU device lookup, device links for thermal/CCI/GPU dependencies, IRQ handling, cpuidle, and optional debugfs. It consumes SoC device-tree nodes and named nvmem cells `svs-calibration-data` and `t-calibration-data`.

## Risks
Incorrect efuse maps, OPP counts, thermal zone names, or bank tables can program invalid voltages. INIT01 temporarily disables OPPs and changes regulator state, so failure cleanup is critical. Two-line high/low bank handling depends on `turn_pt` calculations and can produce inconsistent voltages if OPP ordering changes. IRQ matching relies on bank `int_st` bits and shared hardware register selection under a global spinlock. Thermal errors intentionally move banks to `SVSB_PHASE_ERROR` and restore defaults, reducing optimization. Resource lifetime for `of_iomap()` is manually unwound on probe failure; successful probe does not register an explicit remove path, matching many always-on SoC drivers but making unload behavior dependent on devres/module lifecycle.

## Test Signals
Useful signals are successful probe logs, efuse parse logs, absence of `init01/init02 completion timeout`, OPP count matching platform tables, regulator and PM runtime cleanup on INIT01 failure, monitor interrupts changing OPP voltages, suspend/resume cycling INIT02 and monitor mode, and debugfs `svs/dump` plus per-bank `status` values matching expected OPP voltage bounds.
