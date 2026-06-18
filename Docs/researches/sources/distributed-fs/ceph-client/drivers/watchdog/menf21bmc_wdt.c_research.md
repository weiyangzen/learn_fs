<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/menf21bmc_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/menf21bmc_wdt.c`

Purpose: MEN 14F021P00 BMC watchdog driver using SMBus commands to a parent I2C BMC device.

Important APIs, types, and functions: `struct menf21bmc_wdt` stores watchdog core state and the parent `i2c_client`. Start sends `BMC_CMD_WD_ON`, stop writes `BMC_CMD_WD_OFF` with magic value `0x69`, ping sends `BMC_CMD_WD_TRIG`, set_timeout writes `BMC_CMD_WD_TIME` in 100 ms units, and bootstatus reads `BMC_CMD_RST_RSN`.

Control flow: probe obtains the parent I2C client, allocates state, initializes watchdog bounds, reads the current BMC timeout because BMC persists it across restarts, initializes the watchdog timeout from that value, sets nowayout/drvdata, maps reset reason to bootstatus, registers, and logs enabled state. Shutdown writes the watchdog-off command.

State and persistence: timeout value is stored in the BMC and survives system restart, so probe imports it. Bootstatus is BMC reset-reason state. Stop requires the magic off value.

Dependencies and integration points: depends on platform device under an I2C BMC, SMBus byte/word operations, watchdog core, and platform shutdown.

Risks and test signals: risks include SMBus endianness/word units, persistent BMC timeout surprises, shutdown command using word write for an off command otherwise written as byte-data, and no stop-on-reboot helper. Test BMC timeout import, reset-reason mappings, start/stop/ping SMBus transactions, nowayout, and shutdown on poweroff/reboot.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/menf21bmc_wdt.c -->
