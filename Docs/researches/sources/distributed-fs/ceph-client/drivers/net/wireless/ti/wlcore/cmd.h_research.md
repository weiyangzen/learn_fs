# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/cmd.h

## Purpose
`cmd.h` declares the public wlcore command API and defines the packed firmware command ABI used by `cmd.c` and adjacent wlcore modules. It is the contract between host driver code and wl12xx/wl18xx firmware command mailboxes.

## Important APIs and types
The header exports command functions for command send/configure/interrogate, role start/stop/enable/disable, device role ROC, link allocation/free, template building, key programming, peer state, AP peer add/remove, firmware logging, channel switch stop, regulatory configuration, generic feature configuration, and event waits.

The central ABI types are `struct wl1271_cmd_header`, `struct wl1271_command`, `enum wl1271_commands`, command status constants, `enum cmd_templ`, role structures (`wl12xx_cmd_role_enable`, `wl12xx_cmd_role_disable`, `wl12xx_cmd_role_start`, `wl12xx_cmd_role_stop`), `struct wl1271_cmd_template_set`, `struct wl1271_cmd_ps_params`, `struct wl1271_cmd_set_keys`, peer/ROC structures, firmware logger structures, DFS regulatory config, generic config, and calibration test structures.

## Control flow and integration
Consumers allocate one of these packed structures, fill host-side fields using little-endian conversions where required, and pass it to `wl1271_cmd_send()` or the configure/interrogate wrappers. The firmware command IDs in `enum wl1271_commands` select mailbox behavior, while command status codes returned in `wl1271_cmd_header.status` are validated by `cmd.c`.

## State and persistence behavior
The header does not mutate state directly, but it defines persistent command-visible state: role IDs, HLIDs, sessions, rates, key material, logger mode, channel bitmaps, and feature toggles. These structures are packed, so layout is persistent across host/firmware boundaries and must remain synchronized with firmware expectations.

## Dependencies and risks
It depends on `wlcore.h` and kernel/mac80211 scalar types. The main risks are ABI drift, incorrect enum values, missing `__packed`, wrong endian annotations, and command structures exceeding firmware mailbox limits such as `WL1271_CMD_MAX_PARAMS` or `WL1271_CMD_TEMPL_MAX_SIZE`.

## Test signals
Compile-time structure use, role lifecycle smoke tests, firmware command status validation, key install/remove, AP peer management, and template programming are the primary signals. Firmware rejecting a command with `CMD_STATUS_INVALID_PARAM`, `CMD_STATUS_TEMPLATE_TOO_LARGE`, or `CMD_STATUS_UNKNOWN_CMD` often points back to this ABI layer.
