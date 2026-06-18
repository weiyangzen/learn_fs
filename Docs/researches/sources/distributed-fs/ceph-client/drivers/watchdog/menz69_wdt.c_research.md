<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/menz69_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/menz69_wdt.c`

Purpose: watchdog-core driver for MEN z069 IP-core devices on the MCB bus.

Important APIs, types, and functions: `struct men_z069_drv` stores watchdog core device, MMIO base, and claimed MCB memory resource. `men_z069_wdt_start()` sets `WDEN`, stop clears it, ping toggles the watchdog trigger value by XORing `WVR` with `0xffff`, and set_timeout writes seconds converted at 500 Hz into `WTR` while preserving enable.

Control flow: MCB probe requests the `z069-wdt` memory resource, maps it, initializes timeout bounds from the 15-bit counter, applies watchdog_init_timeout, sets nowayout/drvdata/parent, stores MCB drvdata, and registers with watchdog core. Remove unregisters and releases MCB memory.

State and persistence: hardware state is in `WTR` and `WVR`; timeout counter max is `0x7fff / 500`. No bootstatus is reported. The driver preserves enable state while changing timeout.

Dependencies and integration points: depends on MCB bus device ID `0x45`, MCB memory APIs, MMIO, watchdog core, and namespace import `MCB`.

Risks and test signals: risks include resource release on partial probe, timeout multiplication overflow beyond 15 bits, trigger toggle assumptions, and unregister ordering. Test MCB resource mapping, timeout bounds, start/stop bit preservation, ping toggling, and remove cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/menz69_wdt.c -->
