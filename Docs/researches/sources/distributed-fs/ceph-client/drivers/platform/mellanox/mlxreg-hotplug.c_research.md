# sources/distributed-fs/ceph-client/drivers/platform/mellanox/mlxreg-hotplug.c

## Purpose
Generic Mellanox/Nvidia regmap hotplug driver. It monitors aggregated CPLD interrupt/status registers, exposes component state through hwmon sysfs, sends uevents, and creates or destroys I2C or platform child devices when PSUs, fans, power rails, ASICs, line cards, or other platform elements change state.

## Important APIs, Types, And Functions
`struct mlxreg_hotplug_priv_data` stores platform data, regmap, delayed work, IRQ, hwmon groups, aggregation cache, and recovery counters. `mlxreg_hotplug_device_create()` and `_destroy()` handle I2C/default, platform, no-action, notifier, and uevent paths. `mlxreg_hotplug_attr_init()` builds read-only hwmon attributes. `mlxreg_hotplug_work_handler()`, `_work_helper()`, and `_health_work_helper()` process aggregation bits, group status bits, health state machines, masking, event acknowledgement, and rescheduling.

## Control Flow
Probe validates platform data and deferred adapter availability, requests the IRQ, disables it, builds attributes, registers hwmon, initializes interrupt masks, invokes the worker once to create initially present devices, and enables the IRQ. IRQ handler schedules delayed work. The worker masks aggregation, reads current status, diffs against cached state, handles asserted groups, acknowledges and unmasks events, and reschedules immediate work to catch events that arrived while masked.

## State, Dependencies, Integration, Risks, Tests
State includes per-item caches, attached flags and health counters in platform data, aggregation cache, `not_asserted` recovery count, child client/platform handles, and adapter references. Dependencies include regmap, I2C, platform devices, hwmon, uevents, IRQs, delayed work, and `mlxreg_core_*` platform data. Risks include shared static platform data mutation, missed interrupt recovery relying on repeated scans, incorrect inverted masks creating/destroying wrong devices, hwmon attr count limits, uevent environment lifetime, and cleanup destroying devices that were never attached. Test signals include initial population, insert/remove events, inverted versus normal groups, health good/bad transitions, notifier callbacks, platform-action children, adapter defer, and remove path masking/destroying all attached devices.
