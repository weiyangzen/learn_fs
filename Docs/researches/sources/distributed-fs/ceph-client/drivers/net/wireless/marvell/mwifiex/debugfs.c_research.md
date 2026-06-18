# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/debugfs.c

## Purpose
`debugfs.c` exposes mwifiex runtime state and low-level controls under debugfs. It creates a top-level `mwifiex` directory and per-netdev directories containing readouts for driver/BSS info, firmware statistics, internal debug rings, RX histogram data, version strings, and read/write controls for registers, memory, EEPROM, host-sleep config, debug mask, robust coexistence, histogram reset, and device reset.

## Important APIs, types, and functions
Lifecycle APIs are `mwifiex_debugfs_init()`, `mwifiex_debugfs_remove()`, `mwifiex_dev_debugfs_init()`, and `mwifiex_dev_debugfs_remove()`. Read handlers include `mwifiex_info_read()`, `mwifiex_getlog_read()`, `mwifiex_histogram_read()`, `mwifiex_debug_read()`, `mwifiex_regrdwr_read()`, `mwifiex_debug_mask_read()`, `mwifiex_verext_read()`, `mwifiex_memrw_read()`, `mwifiex_rdeeprom_read()`, `mwifiex_hscfg_read()`, and `mwifiex_timeshare_coex_read()`. Write handlers include `mwifiex_histogram_write()`, `mwifiex_regrdwr_write()`, `mwifiex_debug_mask_write()`, `mwifiex_verext_write()`, `mwifiex_memrw_write()`, `mwifiex_rdeeprom_write()`, `mwifiex_hscfg_write()`, `mwifiex_timeshare_coex_write()`, and `mwifiex_reset_write()`.

## Control flow
Module-level setup calls `mwifiex_debugfs_init()` to create `/sys/kernel/debug/mwifiex`. Per-interface setup calls `mwifiex_dev_debugfs_init()`, which creates a directory named after `priv->netdev->name` and registers files such as `info`, `debug`, `getlog`, `regrdwr`, `rdeeprom`, `memrw`, `hscfg`, `histogram`, `debug_mask`, `timeshare_coex`, `reset`, and `verext`. Removal recursively deletes the per-device directory or top-level directory.

Read handlers allocate a page or stack buffer, query live driver/firmware state, format text with `sprintf`/`snprintf`/`scnprintf`, and return it through `simple_read_from_buffer()`. Write handlers copy user input with `memdup_user_nul()` or typed `kstrto*from_user()` helpers, parse command fields, update saved command parameters or adapter state, and often invoke synchronous firmware commands. `regrdwr` and `rdeeprom` use a write-then-read model where write stores the requested operation in static file-scope variables and subsequent read executes or displays it.

## State and persistence behavior
Debugfs state is live and kernel-resident. File-scope saved variables hold the last register and EEPROM requests globally, not per-interface, which is observable if multiple interfaces use debugfs concurrently. `debug_mask_write()` changes `adapter->debug_mask`; `verext_write()` changes `priv->versionstrsel`; `histogram_write()` resets `priv->hist_data`; `memrw_write()` updates `priv->mem_rw`; `hscfg_write()` can update firmware host-sleep configuration and host-sleep flags; `reset_write()` can trigger bus-level card reset. Debugfs entries disappear when the device/interface is removed.

## Dependencies and integration points
This file depends on Linux debugfs, netdev stats and multicast lists, mwifiex BSS/stat/debug/version helpers, firmware command paths, register/memory/EEPROM accessors, host-sleep helpers, histogram storage defined in `decl.h`, and bus reset support exposed through `adapter->if_ops.card_reset`. `cfg80211.c` calls per-device debugfs init/remove when virtual interfaces are registered/unregistered under `CONFIG_DEBUG_FS`.

## Risks and test signals
The file intentionally exposes powerful diagnostic operations. Risks include global saved register/EEPROM state across interfaces, synchronous firmware commands from debugfs context, page-sized formatted output truncation, command parsing mistakes, and reset/debug-mask controls that can disrupt normal operation. Test signals include reading all debugfs files on disconnected and connected STA, AP mode, multiple virtual interfaces, invalid write payloads, register/memory/EEPROM read/write failure paths, robust-coex on non-v15 firmware, histogram reset, host-sleep configuration, and card reset behavior.
