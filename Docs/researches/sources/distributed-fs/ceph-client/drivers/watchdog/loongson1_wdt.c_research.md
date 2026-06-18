<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/loongson1_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/loongson1_wdt.c`

Purpose: Loongson1/LS2K0300 watchdog-core driver with variant-specific register offsets and enable bits.

Important APIs, types, and functions: `struct ls1x_wdt_pdata` supplies timer, set, and enable-bit layout. `ls1x_wdt_ping()` writes the set register, `ls1x_wdt_set_timeout()` writes clock-rate-scaled counts capped by max hardware heartbeat, start writes the enable bit, stop clears it, and restart enables with a count of one.

Control flow: probe obtains match data, maps MMIO, enables the clock, computes `max_hw_heartbeat_ms`, initializes watchdog defaults and module heartbeat, sets nowayout/drvdata, and registers. PM suspend stops active watchdogs; resume restarts them.

State and persistence: timeout count is stored in hardware timer register; logical timeout can exceed one hardware heartbeat because watchdog core may supervise via `max_hw_heartbeat_ms`. No bootstatus is reported.

Dependencies and integration points: depends on OF compatibles `loongson,ls1b-wdt`, `ls1c-wdt`, `ls2k0300-wdt`, a clock, MMIO, watchdog core, and simple PM ops.

Risks and test signals: risks include incorrect variant offset data, clock-rate overflow, not restoring timeout on resume beyond start, and no reboot stop hook. Test all compatible layouts, timeout counts, restart reset, suspend/resume active state, and heartbeat values above hardware max.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/loongson1_wdt.c -->
