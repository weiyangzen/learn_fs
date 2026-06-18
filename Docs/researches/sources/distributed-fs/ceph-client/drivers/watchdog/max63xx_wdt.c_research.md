<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/max63xx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/max63xx_wdt.c`

Purpose: watchdog-core driver for Maxim MAX6369-6374 external watchdog chips connected through memory-mapped WDI/WDSET pins.

Important APIs, types, and functions: timeout tables describe WDSET pin encodings, initial delay, and watchdog timeout. `max63xx_select_timeout()` chooses a table entry honoring the `nodelay` parameter for MAX6373/74. `max63xx_mmap_ping()` toggles WDI, and `max63xx_mmap_set()` writes WDSET bits under a spinlock. Start programs WDSET and pings edge-triggered no-delay modes; stop selects disabled WDSET value.

Control flow: probe selects a timeout table from OF match data or platform ID, validates/clamps heartbeat, chooses a hardware setting, maps the one-byte resource, initializes watchdog core timeout/info/ops, sets nowayout, registers, and logs selected timeout and initial delay.

State and persistence: hardware timeout is quantized to chip table entries and may be much longer than nominal according to datasheet variation. Driver state stores the selected table entry and MMIO access callbacks. No bootstatus or set_timeout op is provided.

Dependencies and integration points: depends on platform or OF IDs for specific Maxim variants, a memory-mapped byte resource, watchdog core, spinlock-protected raw byte access, and module parameters `heartbeat`, `nowayout`, `nodelay`.

Risks and test signals: risks include board-specific wiring assumptions, timeout tolerance much larger than selected value, nodelay selection failure, and disabling via WDSET not supported on all wiring. Test each variant table, heartbeat requests around available values, MMIO bit preservation, edge-triggered startup ping, and stop/nowayout behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/max63xx_wdt.c -->
