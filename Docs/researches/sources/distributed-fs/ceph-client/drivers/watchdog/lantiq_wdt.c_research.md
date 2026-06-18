<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lantiq_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/lantiq_wdt.c`

Purpose: Lantiq SoC watchdog driver for XRX/Falcon variants, using password-protected control register writes and syscon reset-cause reporting.

Important APIs, types, and functions: `struct ltq_wdt_priv` stores watchdog core state, MMIO base, and divided clock rate. Start/stop/ping use a two-password sequence (`PW1`, then `PW2`) through `ltq_wdt_mask()`. `ltq_wdt_get_timeleft()` reads the status counter. Variant callbacks read reset status from RCU syscon phandles.

Control flow: probe maps watchdog registers, computes watchdog clock from `clk_get_io() / LTQ_WDT_DIVIDER`, initializes timeout to max, reads variant bootstatus, applies nowayout and OF timeout, detects already-enabled watchdog, reprograms it with current settings, marks `WDOG_HW_RUNNING`, and registers.

State and persistence: enable and counter state live in watchdog control/status registers. Reset cause is variant-specific syscon state. If firmware left the watchdog enabled, Linux overwrites settings without a stop and takes ownership.

Dependencies and integration points: depends on Lantiq SoC clock helper, MMIO, syscon/regmap phandles `regmap` or `lantiq,rcu`, OF compatible match data, and watchdog core.

Risks and test signals: risks include broken password sequencing, clock divider too high yielding zero rate, bootstatus phandle differences, and max timeout derived from clock. Test XRX/Falcon reset cause, already-running handoff, get_timeleft, start/ping password writes, and nowayout/module parameter behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lantiq_wdt.c -->
