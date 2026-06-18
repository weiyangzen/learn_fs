# sources/distributed-fs/ceph-client/include/linux/power/charger-manager.h

Purpose: defines the charger-manager framework data model for coordinating multiple charger regulators, cable/extcon events, fuel-gauge status, thermal limits, and suspend-aware charging policy behind one power_supply.

Important APIs and types: enums classify battery-present data source, polling mode, and battery temperature state. `struct charger_cable` binds extcon connector data, work item, notifier, attached state, current limits, parent regulator, and manager. `struct charger_regulator` stores regulator name/consumer, external-control flag, cable array, sysfs attributes, and manager pointer. `struct charger_desc` describes full-battery thresholds, polling, battery-present source, charger status supplies, charger regulators, fuel gauge, thermal zone, temperature limits/hysteresis, measurement source, and max charging/discharging durations. `struct charger_manager` stores runtime list/device/desc, thermal zone, charger state, emergency stop, power_supply desc/instance, charge timing, and battery status.

Control flow: platform code describes chargers, extcon cables, fuel gauge, thermal zone, and thresholds. The charger manager registers a synthetic power_supply, listens for extcon changes, adjusts charger regulators and current limits from cable state, polls or reacts to charger/fuel-gauge changes, stops charging on thermal/emergency/full/duration constraints, and can monitor while suspended using alarms.

State and persistence: runtime state includes attached cable booleans, regulator consumers, sysfs attributes, charger-enabled/emergency-stop flags, timing counters, battery status, work items, notifiers, and power_supply handles. Policy is static platform data; no persistence is stored here.

Dependencies and integration points: integrates with power_supply, extcon, regulator core, alarmtimer, thermal framework, sysfs, workqueues, charger/fuel-gauge supplies, and suspend-to-RAM monitoring.

Risks and test signals: risks include extcon notifier lifetime, regulator current-limit mismatch per cable, hysteresis errors around thermal thresholds, full-battery restart logic, charging duration overflow, externally controlled chargers left disabled/enabled unexpectedly, and missing fuel-gauge/charger supplies. Test cable attach/detach, multi-charger regulator enable/disable, thermal stop/restart, full-charge voltage/SOC/capacity thresholds, suspend alarm monitoring, emergency stop, and sysfs state toggles.
