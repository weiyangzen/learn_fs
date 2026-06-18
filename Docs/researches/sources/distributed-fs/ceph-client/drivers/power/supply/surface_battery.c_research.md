# sources/distributed-fs/ceph-client/drivers/power/supply/surface_battery.c

## Purpose
Microsoft Surface battery driver using the Surface System Aggregator Module. It maps SSAM battery status/static/dynamic requests to power_supply properties for Surface devices with BAT1 and Surface Book BAT2 batteries.

## Important APIs, Types, and Functions
`struct spwr_bix` and `struct spwr_bst` mirror ACPI `_BIX` and `_BST` payloads. `struct spwr_battery_device` stores the SSAM device, power supply descriptor, delayed update work, event notifier, mutex-protected cached `sta`, `bix`, `bst`, timestamp, and alarm threshold. Important functions include `spwr_battery_register()`, `spwr_battery_get_property()`, `spwr_notify_bat()`, `spwr_battery_update_bix_unlocked()`, `spwr_battery_update_bst_unlocked()`, alarm sysfs handlers, and resume/remove callbacks.

## Control Flow
Probe selects match data, initializes the battery object/notifier, validates `_STA`, loads `_BIX` and `_BST`, initializes the alarm to design warning capacity when present, selects charge or energy property sets based on power unit, registers the power supply, and registers an SSAM notifier. Property reads refresh `_BST` if the cache expired, reject non-present batteries except `PRESENT`, and convert little-endian SSAM fields into power_supply units. SSAM events refresh static or dynamic state and notify the power supply; external power changes schedule a delayed refresh for EC update latency.

## State and Persistence
The driver caches EC state for `cache_time` milliseconds under `lock`. `alarm` is stored in software and programmed to EC via `_BTP`. No disk persistence is used; state is reloaded from SSAM/EC on probe and resume.

## Dependencies and Integration Points
Depends on SSAM request/notifier APIs, power_supply, delayed work, sysfs attributes, jiffies cache timing, and unaligned little-endian access helpers. Device IDs match BAT/SAM and BAT/KIP instances.

## Risks and Test Signals
Event registration must use instance 0 and manually filter event instance IDs. Unit changes after registration are only warned via `WARN_ON`. Cached `_BST` can temporarily serve stale values. Test present/absent battery behavior, both mW and mA power-unit property sets, alarm read/write, SSAM event handling, external-power delayed refresh, resume recheck, and notifier unregister/work cancellation.
