<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/rk3399_dmc.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/rk3399_dmc.c

Purpose: Rockchip RK3399 DMC devfreq driver. It scales DDR frequency and center voltage using simple-ondemand decisions driven by a Rockchip DFI devfreq-event provider, and programs DDR power-down/ODT timings through Trusted Firmware SMC calls.

Important APIs and control flow: probe obtains `center` regulator, `dmc_clk`, DFI event provider, enables events, reads optional timing properties, reads DDR type and ODT disable frequency from PMU GRF when present, initializes firmware DRAM config, loads OPPs, gets current rate/voltage, registers a simple-ondemand devfreq profile, and registers an OPP notifier. `rk3399_dmcfreq_target()` selects target OPP, blocks Rockchip PMU power-domain transitions, computes idle/ODT arguments from target DDR controller MHz, sends SMC timing updates, raises voltage before scaling up, calls `clk_set_rate()`, verifies the actual clock, scales voltage down after scaling down, updates cached rate/voltage, and unblocks PMU. Status reads DFI event counts. Suspend disables the event provider and suspends devfreq; resume re-enables both.

State and persistence behavior: per-device state includes devfreq profile/device, simple-ondemand data, DMC clock, event provider, mutex, center regulator, PMU regmap, cached current and target rate/voltage, and DT timing thresholds. Event provider state persists separately in `rockchip-dfi.c`.

Dependencies and integration points: depends on devfreq core/simple-ondemand, devfreq-event DFI provider, OPP/regulator/clock, Rockchip PM domains, syscon GRF, SMCCC Rockchip SIP, and compatible `rockchip,rk3399-dmc`.

Risks and test signals: `rk3399_dmcfreq_of_props()` ORs optional property failures and the return is ignored, so missing timing properties become zero values. If `devfreq_suspend_device()` fails after event disable, resume expectations can be uneven. Voltage rollback after failed clock set assumes cached voltage is still valid. Test signals include DFI event deferral and enable/disable balance, DDR type-specific ODT thresholds, SMC timing arguments, PMU block/unblock pairing, clock-rate verification, voltage sequencing on up/down transitions, suspend/resume, and simple-ondemand response to memory traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/rk3399_dmc.c -->
