<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/m54xx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/m54xx_wdt.c`

Purpose: legacy miscdevice watchdog for ColdFire MCF547x/MCF548x processors using GPT0 watchdog bits.

Important APIs, types, and functions: `wdt_enable()` preserves GPT GPIO settings, programs `GCIR0` from `heartbeat` and bus clock, and sets watchdog enable/count enable with the output compare password. `wdt_disable()` clears enable bits. `wdt_keepalive()` rewrites the password bit. File operations implement single-open, magic close, ioctls, and keepalive writes.

Control flow: init reserves the GPT counter register region and registers `/dev/watchdog`. Open sets in-use state, clears OK-to-close, and enables hardware. Writes scan for `V` when not nowayout and ping. Ioctl supports support/status/bootstatus/keepalive/set/get timeout with max 30 seconds. Release disables only when magic close was seen; otherwise it pings and leaves the watchdog running.

State and persistence: state is tracked with `wdt_status` bits `WDT_IN_USE` and `WDT_OK_TO_CLOSE`, plus global heartbeat/nowayout. Bootstatus is not available. Hardware GPT configuration may preserve pre-existing GPIO usage.

Dependencies and integration points: depends on ColdFire architecture headers/registers, misc watchdog ABI, raw MMIO access, and module parameters.

Risks and test signals: risks include bus-clock math, preserving GPIO mode incorrectly, heartbeat maximum mismatch, and legacy close semantics. Test region reservation, magic close versus unexpected close, set_timeout reprogramming, keepalive writes, nowayout module pinning behavior, and GPT register values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/m54xx_wdt.c -->
