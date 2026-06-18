# sources/distributed-fs/ceph-client/drivers/power/supply/huawei-gaokun-battery.c

Purpose: implements adapter and battery power supplies for Huawei Matebook E Go systems using the Gaokun EC auxiliary device. It reports EC battery/adapter data and exposes Huawei smart/adaptive charge controls.

Important APIs/types/functions: `struct gaokun_psy` stores EC pointer, notifier, adapter/battery supplies, cached battery status/info blocks, strings, charge state, online state, and presence. `gaokun_psy_get_adp_property()` reports USB-C adapter online/type. `gaokun_psy_get_bat_property()` reports status, presence, technology, cycle count, voltage/current/charge/capacity, thresholds, and strings. Sysfs attributes are `battery_adaptive_charge` and `smart_charge_delay`.

Control flow: probe registers adapter and battery supplies, attaches smart-charge sysfs groups to the battery supply, initializes presence/info/vendor/model/serial caches, and registers for EC notifications. Battery property reads refresh cached status if present and cache time expired. Smart-charge threshold setters read the EC smart-charge buffer, adjust start/end ordering, and write it back. EC notifications refresh adapter or battery caches and emit `power_supply_changed()` for relevant events.

State and persistence: cached EC data is valid for `CACHE_TIME` milliseconds. Smart-charge enable, delay, and thresholds are persisted/owned by EC firmware after setter calls. The driver mutates the model string by forcing byte 14 to `A` as a local fixup.

Dependencies and integration: depends on the Gaokun EC platform API, auxiliary bus matching, notifier registration, power-supply core, little-endian packed EC data layouts, and EC smart-charge helper functions.

Risks and test signals: this snapshot duplicates the battery-present check in `gaokun_psy_get_bat_property()`. Threshold setters can overflow/underflow when asked to set start above 99 or end below 1 because they adjust the opposite threshold by plus/minus one without explicit bounds checks. Test absent battery, cache expiration, EC event ordering/delays, smart-charge sysfs parsing, threshold boundaries, string reads/model fixup, notifier unregister, and EC read/write failures.
