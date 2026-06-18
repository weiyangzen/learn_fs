# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/vendor_cmd.c

## Purpose
`vendor_cmd.c` registers TI vendor commands and events on the wlcore wiphy. The commands expose smart-config firmware features through cfg80211/nl80211 vendor command hooks: start smart config, stop smart config, and set a smart-config group key.

## Important APIs And Functions
- `wlcore_vendor_attr_policy[]` accepts `WLCORE_VENDOR_ATTR_FREQ`, `WLCORE_VENDOR_ATTR_GROUP_ID`, and binary `WLCORE_VENDOR_ATTR_GROUP_KEY` up to `WLAN_MAX_KEY_LEN`.
- `wlcore_vendor_cmd_smart_config_start()` parses a required group ID and calls `wlcore_smart_config_start()`.
- `wlcore_vendor_cmd_smart_config_stop()` calls `wlcore_smart_config_stop()` without attributes.
- `wlcore_vendor_cmd_smart_config_set_group_key()` parses required group ID and group key, then calls `wlcore_smart_config_set_group_key()`.
- `wlcore_set_vendor_commands()` assigns command and event arrays to `wiphy->vendor_commands`, `wiphy->n_vendor_commands`, `wiphy->vendor_events`, and `wiphy->n_vendor_events`.

## Control Flow
Each command handler converts `wiphy` to `ieee80211_hw`, then to `struct wl1271`. Attribute-bearing commands reject missing data, parse netlink attributes with the local policy, and require the needed attributes. All handlers lock `wl->mutex`, reject devices not in `WLCORE_STATE_ON`, resume runtime PM with `pm_runtime_resume_and_get()`, invoke the chip op wrapper, autosuspend the device, unlock, and return the chip-op status.

## State And Persistence Behavior
The file does not own long-lived state. It mutates only cfg80211 registration fields on the `wiphy`. Command effects are delegated to chip ops and firmware. The only runtime state checks are `wl->state` and runtime PM references.

## Dependencies And Integration Points
This file depends on cfg80211 vendor command infrastructure, netlink attribute parsing, mac80211 `wiphy_to_ieee80211_hw()`, runtime PM, and wlcore chip-op wrappers from `hw_ops.h`. Registration is called from wlcore setup in `main.c`. Smart-config implementation is optional per chip; wl18xx supplies these ops, while wrappers can report unsupported behavior if ops are absent.

## Risks And Test Signals
Risks include ABI compatibility with userspace vendor commands, accepting unused attributes from `vendor_cmd.h` without policy coverage, missing runtime-PM put paths, and chip ops being unavailable. Test by issuing valid and invalid nl80211 vendor commands, verifying `-EINVAL` for missing data/group/key or off-state devices, checking runtime PM balance, and observing smart-config vendor events (`SC_SYNC`, `SC_DECODE`) from firmware-capable devices.
