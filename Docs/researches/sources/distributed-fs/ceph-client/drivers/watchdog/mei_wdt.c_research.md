<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mei_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/mei_wdt.c`

Purpose: Intel MEI iAMT watchdog driver that exposes a firmware-managed AMT watchdog through the watchdog core and dynamically registers/unregisters depending on firmware "watchdog required" state.

Important APIs, types, and functions: `struct mei_wdt` stores watchdog core object, MEI client, internal state, response completion, unregister work, registration lock, timeout, and optional debugfs. Packed MEI Management Control request/response structs encode start/ping and stop commands. `mei_wdt_ops_start()` transitions to START; ping sends start/ping and optionally waits for a response; stop sends stop only from RUNNING. RX callback validates firmware responses and reacts to `MEI_WDT_WDSTATE_NOT_REQUIRED`.

Control flow: probe allocates state, enables the MEI client, registers RX and notification callbacks, records firmware version, and either pings firmware for a response-required probe or registers immediately for legacy firmware. RX during PROBE stops firmware watchdog and registers if required, or marks NOT_REQUIRED. RX during RUNNING may schedule unregister work to avoid watchdog-core deadlock. Remove completes any waiter, cancels work, unregisters, disables MEI, removes debugfs, and frees state.

State and persistence: the authoritative watchdog is in Intel ME/AMT firmware. Driver state machine values are PROBE, IDLE, START, RUNNING, STOPPING, and NOT_REQUIRED. Registration state is guarded by `reg_lock`, and drvdata being non-NULL means registered. Firmware version controls whether ping responses are required.

Dependencies and integration points: depends on MEI client bus UUID `05B79A6F-4628-4D7F-899D-A91514CB32AB`, watchdog core, MEI send/recv/notif APIs, completions/workqueue, and optional debugfs files `state` and `activation`.

Risks and test signals: risks include response wait interruption, dynamic unregister during pings, firmware declaring watchdog not required, deadlock if unregister happens in RX context, and global `wd_info.firmware_version` mutation. Test legacy and response-required firmware, NOT_REQUIRED transitions and notification reactivation, stop while not running, debugfs state, MEI reset/remove with outstanding completion, and min timeout enforcement at 120 seconds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mei_wdt.c -->
