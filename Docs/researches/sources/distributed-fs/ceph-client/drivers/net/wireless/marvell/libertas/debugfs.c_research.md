## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/debugfs.c

Purpose: this file creates Libertas debugfs control/status files under `lbs_wireless/<netdev>/`. It exposes device info, sleep parameters, host sleep, firmware event subscriptions, raw MAC/BBP/RF register access, and optional debug fields when `PROC_DEBUG` is enabled.

Important APIs and functions: global lifecycle is `lbs_debugfs_init()`/`lbs_debugfs_remove()`, while per-device lifecycle is `lbs_debugfs_init_one()`/`lbs_debugfs_remove_one()`. File handlers include `lbs_dev_info()`, sleep parameter read/write, host sleep read/write, `lbs_threshold_read()`/`lbs_threshold_write()` for RSSI/SNR/fail/beacon events, register read/write handlers for MAC/BBP/RF, and optional `lbs_debugfs_read()`/`lbs_debugfs_write()` for selected `lbs_private` fields.

Control flow: init creates a root directory, per-device directory, base files, `subscribed_events`, and `registers`. Reads allocate one page, issue command helpers where needed, format values, and copy to userspace. Writes parse user input with `sscanf()`/`simple_strtoul()`, then issue firmware commands or update offsets. Event subscription writes first read current subscription state, update a mask, build one TLV, and write it back.

State and persistence: debugfs state is in dentries stored in `lbs_private`; actual settings affect firmware (`CMD_802_11_SLEEP_PARAMS`, host sleep, subscribe events, register writes) or driver offsets (`mac_offset`, `bbp_offset`, `rf_offset`). State is not persistent across driver reloads.

Dependencies and integration: depends on debugfs, command helpers in `cmd.c`, host TLV structs, `lbs_private`, and netdev names. It is diagnostic but can materially change hardware behavior.

Risks and tests: raw register writes are privileged and hazardous. Parser bounds rely on page-sized `memdup_user_nul()` limits. Optional debug `items[]` mutates stored offsets by adding `priv`, so multiple init paths would be risky. Test signals include debugfs tree creation/removal, valid/invalid writes, firmware command failures, register read/write behavior, and module unload without dangling dentries.
