# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/testmode.c

## Purpose
`testmode.c` implements cfg80211 testmode commands for factory/diagnostic access to wlcore firmware. It allows privileged userspace to send raw test commands, interrogate/configure firmware IEs, switch PLT modes, run FEM detection, and read fuse-derived MAC addresses while in PLT.

## Important APIs, Types, and Functions
The public entry point is `wl1271_tm_cmd()`, registered through `CFG80211_TESTMODE_CMD` in `main.c`. Internal command IDs include TEST, INTERROGATE, CONFIGURE, SET_PLT_MODE, and GET_MAC, with legacy unused IDs retained for ABI compatibility. `wl1271_tm_policy` validates netlink attributes. `wl1271_tm_cmd_test()` sends raw test command buffers through `wl1271_cmd_test()` and optionally returns the answer. `wl1271_tm_cmd_interrogate()` allocates a `struct wl1271_command`, calls `wl1271_cmd_interrogate()`, and replies with command data. `wl1271_tm_cmd_configure()` sends `wl1271_cmd_configure()`. `wl1271_tm_cmd_set_plt_mode()` dispatches to `wl1271_plt_start()`/`wl1271_plt_stop()`; FEM detect always stops PLT afterward. `wl12xx_tm_cmd_get_mac()` returns fuse OUI/NIC as an Ethernet address when in PLT.

## Control Flow
`wl1271_tm_cmd()` parses netlink attributes, requires a command ID, blocks all commands except SET_PLT_MODE while in `PLT_CHIP_AWAKE`, and dispatches. Most firmware-touching commands lock `wl->mutex`, verify `WLCORE_STATE_ON` where needed, resume runtime PM, call command helpers, create a cfg80211 testmode reply SKB if data is returned, and put runtime PM.

## State and Persistence Behavior
The file changes PLT state through `main.c` helpers and reads fuse MAC fields from `struct wl1271`. It does not persist data. It may expose firmware command results or calibration status to userspace through netlink replies.

## Dependencies and Integration Points
Dependencies include cfg80211 testmode/genetlink, runtime PM, slab allocation, `wlcore.h`, `debug.h`, `acx.h`, `io.h`, and firmware command helpers. It integrates with PLT lifecycle in `main.c` and factory tools using cfg80211 testmode ABI.

## Risks and Test Signals
Risks include ABI breakage of command/attribute IDs, raw command misuse, insufficient state gating for configure versus test/interrogate, reply buffer sizing, and PLT mode transitions leaving the device unavailable for normal mac80211. Tests should cover each command ID, missing/oversized attributes, PLT_ON/OFF/CHIP_AWAKE/FEM_DETECT transitions, get-mac failure outside PLT, and answer payload delivery.
