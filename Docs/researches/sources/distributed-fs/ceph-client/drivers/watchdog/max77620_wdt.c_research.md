<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/max77620_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/max77620_wdt.c`

Purpose: Maxim MAX77620/MAX77714 PMIC watchdog driver using the parent MFD regmap and variant-specific register layouts.

Important APIs, types, and functions: `struct max77620_variant` describes ONOFF/CNFG registers, WDT clear mask, reset-wake bit, and auto-clear bits. Start/stop toggle `MAX77620_WDTEN`; ping writes the WDTC bit; set_timeout maps requested seconds to fixed 2/16/64/128 second hardware choices and clears the watchdog before changing TWD.

Control flow: probe obtains variant data from platform ID and parent regmap, enables watchdog-reset wake, sets auto-clear bits for sleep/off modes where supported, reads existing config to infer current timeout and running state, marks `WDOG_HW_RUNNING` if enabled, sets nowayout/drvdata, installs stop-on-unregister, and registers.

State and persistence: PMIC registers hold timeout, enable, and reset behavior across Linux driver lifetime and possibly across warm boot depending on PMIC state. Timeout values are rounded upward to one of four hardware settings. There is no bootstatus reporting.

Dependencies and integration points: depends on parent MAX77620/MAX77714 MFD regmap, platform device IDs, watchdog core, and PMIC register definitions.

Risks and test signals: risks include variant register mismatch, timeout rounding surprises, write ordering around WDTC/TWD, and stop-on-unregister interacting with nowayout expectations. Test both variants, existing enabled watchdog handoff, timeout bucket selection, ping writes, sleep/off auto-clear behavior, and register error propagation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/max77620_wdt.c -->
