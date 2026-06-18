<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/jz4740_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/jz4740_wdt.c`

Purpose: watchdog-core driver for Ingenic JZ4740/JZ4780 watchdogs hosted in the TCU syscon/regmap block.

Important APIs, types, and functions: `struct jz4740_wdt_drvdata` stores watchdog core device, parent TCU regmap, watchdog clock, and clock rate. Ping writes `TCU_REG_WDT_TCNT = 0`; set_timeout disables `TCER`, writes `TDR`, clears counter, then restores enable if it was set; start enables the clock and counter; stop clears counter enable and disables the clock; restart starts with timeout zero.

Control flow: probe gets the `wdt` clock, rounds and sets it to the smallest possible rate, computes timeout bounds from 16-bit hardware, obtains the parent regmap with `device_node_to_regmap()`, sets nowayout/drvdata, and registers.

State and persistence: active state is in TCU `TCER` and clock enable state. Timeout is limited by `0xffff / clk_rate`; the default heartbeat is clamped into supported bounds. There is no bootstatus handling.

Dependencies and integration points: depends on OF compatibles `ingenic,jz4740-watchdog`/`jz4780`, TCU MFD regmap in the parent node, and a controllable watchdog clock.

Risks and test signals: risks include clock-rate rounding failures, timeout truncation through `u16`, parent regmap absence, and restart behavior with zero timeout. Test clock setup, start/stop clock balancing, timeout bounds, active set_timeout preserving enable state, and watchdog reset through restart.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/jz4740_wdt.c -->
