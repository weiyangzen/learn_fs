# sources/distributed-fs/ceph-client/drivers/power/supply/surface_charger.c

## Purpose
`surface_charger.c` exposes the AC adapter state on 7th-generation Microsoft Surface devices through the Surface System Aggregator Module (SSAM). It registers a `POWER_SUPPLY_TYPE_MAINS` device named from match data, currently `ADP1`, and translates SSAM battery `_STA` and power-source requests into a standard `POWER_SUPPLY_PROP_ONLINE` property.

## Important APIs, Types, And Functions
The file is built around SSAM request helpers `ssam_bat_get_sta` and `ssam_bat_get_psrc`, `struct spwr_ac_device`, `struct spwr_psy_properties`, and an `ssam_event_notifier`. `spwr_ac_update_unlocked()` refreshes cached adapter state under `ac->lock`; `spwr_ac_recheck()` updates state and emits `power_supply_changed()` on transitions; `spwr_notify_ac()` handles SSAM battery adapter events; `spwr_ac_get_property()` serves the power-supply core. Probe uses `ssam_device_get_match_data()`, `devm_power_supply_register()`, and `ssam_device_notifier_register()`.

## Control Flow
Probe fetches match properties, allocates `spwr_ac_device`, initializes the notifier and power-supply descriptor, validates the SSAM battery device via `_STA`, registers the mains supply, then subscribes to SSAM adapter-change events. Runtime property reads lock the device, synchronously query `_PSR`, update the cached little-endian state, and return online as a boolean. SSAM event delivery logs the event, accepts all targets and instances for command `SAM_EVENT_CID_BAT_ADP`, rechecks state, and maps any error to an SSAM notifier return. Resume also calls `spwr_ac_recheck()` to refresh userspace after sleep.

## State, Persistence, And Dependencies
Persistent runtime state is only the cached `__le32 state`, the notifier registration, and power-supply registration; no nonvolatile state is written. A mutex protects `state`. The driver depends on the SSAM bus/device framework, SSAM event registry semantics, power-supply class, and Surface BAT target-category commands.

## Integration Points
It supplies batteries named `BAT1` and `BAT2`, uses `module_ssam_device_driver()`, and matches `SSAM_SDEV(BAT, SAM, 0x01, 0x01)`. Its PM hook is a resume refresh, not a suspend action. Removal unregisters the SSAM notifier; devm resources release the supply and memory.

## Risks
`spwr_ac_get_property()` returns early for any nonzero `spwr_ac_update_unlocked()` value, so a successful state change (`status > 0`) can make an `ONLINE` read return `1` instead of filling `val`; this is worth checking against the intended "changed" convention. Listening to all event target/instance pairs is intentional but can overnotify. The state is only as accurate as synchronous SSAM command success; transient command failures propagate to sysfs reads.

## Test Signals
Exercise probe rejection on bad `_STA`, normal registration with `ADP1`, `ONLINE` reads across `_PSR` zero/nonzero values, SSAM adapter event delivery with varied target/instance ids, notifier unregister on remove, and resume-triggered `power_supply_changed()` after a state transition.
