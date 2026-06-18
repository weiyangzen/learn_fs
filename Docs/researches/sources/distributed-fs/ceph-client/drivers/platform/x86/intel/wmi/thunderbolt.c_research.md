<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/thunderbolt.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/thunderbolt.c

Purpose: WMI driver exposing a write-only `force_power` sysfs attribute for selected systems with Intel Thunderbolt force-power WMI GUID `86CCFD48-205E-4A77-9C48-2021CBEDE341`. It lets userspace force Thunderbolt controller power for firmware update or maintenance scenarios.

Important APIs/functions: `force_power_store()` parses the first input character with `hex_to_bin()`, accepts only 0 or 1, and calls `wmidev_invoke_procedure()` with method/block identifiers `0, 1`. The `wmi_driver` declares `dev_groups = tbt_groups` and `no_singleton = true`.

Control flow: the WMI core binds matching GUID devices and creates the attribute. Each write constructs a one-byte WMI buffer and invokes the firmware procedure. There is no probe/remove callback because no driver-private state is needed.

State/persistence: requested force-power mode is stored/applied by firmware. The driver maintains no cached state and exposes no readback.

Dependencies/integration: depends on ACPI WMI and sysfs. Consumers are userspace tools that need Thunderbolt power control when no device is attached.

Risks: input parsing only looks at `buf[0]`, so strings beginning with `0` or `1` are accepted regardless of trailing characters. Firmware behavior is platform-specific and may power hardware unexpectedly. No readback means userspace must trust invocation success.

Test signals: matching WMI device should expose `force_power`; writes beginning with `0` or `1` should call the procedure; non-hex or values above 1 should return `-EINVAL`; WMI invocation failures should propagate negative errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/thunderbolt.c -->
