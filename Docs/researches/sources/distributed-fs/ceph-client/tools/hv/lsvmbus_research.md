# sources/distributed-fs/ceph-client/tools/hv/lsvmbus

## Purpose

`lsvmbus` is a Python 3 diagnostic utility that lists Hyper-V VMBus devices visible in sysfs. It maps well-known Hyper-V class GUIDs to readable device descriptions and prints channel-to-CPU mappings at higher verbosity.

## Important APIs and Flow

The script uses `optparse` for `-v/--verbose`, reads `/sys/bus/vmbus/devices`, and uses `get_vmbus_dev_attr` to read attributes such as `id`, `class_id`, `device_id`, and `channel_vp_mapping`. It builds lightweight `VMBus_Dev` objects, sorts them by numeric VMBus ID, and prints three output formats: terse description, class ID with mapping, or class ID, device ID, sysfs path, and mapping.

## State, Dependencies, and Integration

There is no persistent state. Runtime state is derived entirely from sysfs. It depends on the Hyper-V bus being present and exposing expected attributes. It integrates with `vmbus_testing` and administrator workflows by giving users the device identity and sysfs paths needed for further inspection.

## Risks and Test Signals

The script assumes each device has readable `id`, `class_id`, and `device_id`; missing attributes can raise indexing errors. It sorts mapping lines by the left side of `relid:cpu`, so malformed entries also fail. Tests should run on a Hyper-V guest, on a fake sysfs tree via refactoring or monkeypatching, and with verbosity levels 0, 1, and 2. Compatibility tests should include unknown class IDs and devices without channel mappings.
