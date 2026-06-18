<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/proc.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/proc.c

## Purpose
`proc.c` provides the legacy `/proc/acpi/wakeup` interface. It displays ACPI wake-capable devices, their target sleep state, enable status, and associated physical sysfs devices, and lets userspace toggle wake enablement by writing an ACPI bus ID.

## Important APIs, Types, and Functions
The proc entry uses `acpi_system_wakeup_device_proc_ops`. Important functions are `acpi_system_wakeup_device_seq_show()`, `physical_device_enable_wakeup()`, `acpi_system_write_wakeup_device()`, `acpi_system_wakeup_device_open_fs()`, and `acpi_sleep_proc_init()`.

## Control Flow and State
Init creates `wakeup` under `acpi_root_dir` with mode `0644`. Reads use `single_open()` and iterate `acpi_wakeup_device_list` under `acpi_device_lock`, skipping invalid wake devices. For each ACPI device, output includes bus ID, `S` sleep state, enabled/disabled state, and either no physical node or each linked physical device's bus/name. Writes copy at most four bytes from userspace, parse a bus ID token, lock the wakeup list, find the matching ACPI device, and toggle wakeup on the ACPI device itself if possible or on all wake-capable physical nodes otherwise.

## State and Persistence
The file does not own wake state; it toggles `device_may_wakeup` flags on ACPI or physical devices. The visible list is backed by global ACPI wakeup device registration state.

## Dependencies and Integration Points
Dependencies include procfs, seq_file, ACPI wakeup device lists, device wakeup core APIs, physical-node links, and ACPI sleep initialization. It is a compatibility interface alongside sysfs power/wakeup controls.

## Risks and Test Signals
Risks include four-character bus ID matching via `strncmp()`, writes toggling all physical devices when the ACPI device itself cannot wake, output status combining ACPI and physical wake states, and legacy proc permissions allowing root-driven wake toggles outside sysfs. Test signals are `/proc/acpi/wakeup` formatting, toggling entries by bus ID, matching sysfs `power/wakeup` state changes, correct output for devices with multiple physical nodes, and stable locking while devices are added or removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/proc.c -->
