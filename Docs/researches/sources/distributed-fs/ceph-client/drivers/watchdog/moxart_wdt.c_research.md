<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/moxart_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/moxart_wdt.c`

Purpose: MOXA ART SoC watchdog driver using simple MMIO count/mode/enable registers and watchdog core restart support.

Important APIs, types, and functions: `struct moxart_wdt_dev` stores watchdog core device, MMIO base, and clock frequency. Start writes `clock_frequency * timeout` to count, magic mode `0x5ab9`, and enable `0x03`; stop writes zero to enable; set_timeout only updates the core timeout; restart programs count one and enables reset.

Control flow: probe maps MMIO, gets the clock and validates frequency, computes max timeout from `UINT_MAX / clock_frequency`, initializes watchdog core defaults with optional module heartbeat, sets nowayout and restart priority, installs stop-on-unregister, registers, and logs debug state.

State and persistence: timeout count is only written on start or restart; changing timeout while running updates software state but does not immediately reprogram hardware because set_timeout does not restart or write registers. No bootstatus/timeleft is provided.

Dependencies and integration points: depends on OF compatible `moxa,moxart-watchdog`, a clock, MMIO, watchdog core, and restart priority 128.

Risks and test signals: risks include set_timeout while active not affecting hardware until restart/start, clock frequency overflow, and no stop-on-reboot. Test active timeout changes, start/restart register sequence, stop-on-unregister, heartbeat module parameter, and reset behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/moxart_wdt.c -->
