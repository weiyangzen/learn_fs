# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/debug.h

## Purpose
`debug.h` centralizes wlcore logging names, debug-level bitmasks, and logging/dump macros. It provides a uniform driver prefix and gates verbose debug output through the global `wl12xx_debug_level`.

## Important APIs and types
The debug categories include IRQ, SPI, boot, mailbox, testmode, event, TX, RX, scan, crypto, PSM, mac80211, command, ACX, SDIO, filters, ad-hoc, AP, probe, IO, master, and all. Macros include `wl1271_error()`, `wl1271_warning()`, `wl1271_notice()`, `wl1271_info()`, `wl1271_debug()`, `wl1271_dump()`, and `wl1271_dump_ascii()`.

## Control flow and integration
All wlcore modules call these macros inline. With `CONFIG_DYNAMIC_DEBUG`, `wl1271_debug()` emits through `dynamic_pr_debug()` when the category is enabled. Otherwise it uses `printk(KERN_DEBUG)`. Hex dump helpers cap dumps with `DEBUG_DUMP_LIMIT`.

## State and persistence behavior
The only shared state is external `u32 wl12xx_debug_level`, generally controlled through module/debug mechanisms. The header itself has no persistence, but enabled categories can materially affect diagnostics and log volume.

## Dependencies and risks
It depends on kernel `bitops`, `printk`, dynamic debug, and hex dump helpers. Risks are mainly operational: logging sensitive key material through `DEBUG_CRYPT`, excessive debug volume, and losing diagnostics when category masks are not enabled.

## Test signals
Compile-time macro expansion across modules, dynamic debug behavior, category-gated command/event/IO logs, and bounded hex dump lengths are the main signals.
