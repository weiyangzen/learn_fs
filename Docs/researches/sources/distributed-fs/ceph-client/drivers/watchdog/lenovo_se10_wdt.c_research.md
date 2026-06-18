<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lenovo_se10_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/lenovo_se10_wdt.c`

Purpose: Lenovo SE10 watchdog driver for specific DMI-matched systems using Super I/O BRAM and EC command ports.

Important APIs, types, and functions: `set_bram()` writes watchdog control/config bytes through the BRAM base discovered from Super I/O. `send_cmd()` waits on EC input/output buffer flags. Watchdog ops start by writing `CUS_WDT_SWI=0x80`, stop writes zero, set_timeout writes `CUS_WDT_CFG`, get_timeleft sends `CUS_WDT_CNT`, and ping sends `CUS_WDT_FEED`.

Control flow: module init uses DMI callbacks to create a platform device for supported Lenovo product names. Probe reserves Super I/O config ports, verifies chip ID `0x5632`, reads BRAM base from LDN 0x10, initializes watchdog defaults and nowayout, programs the default timeout, installs stop-on-reboot/unregister, and registers.

State and persistence: global `bram_base` stores the hardware access window. Timeout and enable state are stored in board controller BRAM/EC state. The driver does not read bootstatus. EC buffer waits are bounded by `MAX_WAIT` loops but `wait_for_buffer()` itself returns no status.

Dependencies and integration points: depends on DMI product IDs 12NH/12NJ/12NK/12NL/12NM, x86 I/O ports, Super I/O config mode, watchdog core, and EC command protocol.

Risks and test signals: risks include DMI over/under matching, silent EC wait timeout, BRAM base discovery errors, and no locking around global BRAM base beyond muxed regions. Test DMI creation/removal, chip ID mismatch, timeout 1-255 bounds, get_timeleft EC command, ping under load, and stop-on-reboot/unregister.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lenovo_se10_wdt.c -->
