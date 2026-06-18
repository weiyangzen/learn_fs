<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-wmi-platform.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/msi-wmi-platform.c

## Purpose
This MSI WMI platform driver exposes fan speed readings through hwmon and creates debugfs endpoints for MSI's generic WMI method interface.

## Important APIs, Types, And Functions
`enum msi_wmi_platform_method` enumerates method IDs from package, EC, BIOS, SMBus, battery, thermal, fan, device, power, debug, AP, data, and WMI operations. `struct msi_wmi_platform_data` stores the WMI device and a mutex required because the firmware method is not thread-safe. `msi_wmi_platform_query()` serializes WMI method calls and validates 32-byte ACPI buffer replies with `msi_wmi_platform_parse_buffer()`. `msi_wmi_platform_read()` implements hwmon fan input conversion. Debugfs uses `struct msi_wmi_platform_debugfs_data` plus file operations to write a 32-byte payload and read the last response.

## Control Flow
Module init gates on MSI DMI vendor unless `force=1`, then registers a WMI driver for GUID `ABBC0F6E-8EA1-11D1-00A0-C90629100000`. Probe initializes state and mutex, checks WMI interface major version, checks EC information and Tiger Lake flag, creates debugfs files for all methods, then registers hwmon with four fan input channels.

## State And Persistence
Runtime state is WMI device data, a mutex, and per-debugfs response buffers protected by rwsems. Fan values are read live from firmware. Debugfs stores only the last method response per file.

## Dependencies And Integration Points
Dependencies include WMI, DMI, hwmon, debugfs, mutex/rwsem locking, unaligned big-endian reads, and ACPI buffer behavior. The GUID is generic Microsoft sample-derived, so DMI gating prevents binding to non-MSI firmware that reused it.

## Risks And Edge Cases
The firmware method is explicitly not thread-safe, making the mutex critical. The reply parser treats first response byte `0` as `-EIO`. Debugfs allows raw privileged calls to all methods and can change firmware state through `set_*` methods. Interface and EC checks can be overridden by unsafe `force`.

## Test Signals
Validation should cover DMI whitelist, interface version rejection and force override, non-Tiger Lake rejection, fan RPM conversion including zero divisor, debugfs exact 32-byte write requirement, concurrent debugfs/hwmon access serialization, and cleanup of debugfs on device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-wmi-platform.c -->
