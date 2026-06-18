## sources/distributed-fs/ceph-client/drivers/hwmon/dell-smm-hwmon.c

### Purpose

`dell-smm-hwmon.c` exposes Dell firmware thermal and fan controls through hwmon, optional `/proc/i8k`, and thermal cooling devices. It supports legacy CPU0 SMM I/O traps and a newer WMI-wrapped SMM backend. It reports temperature sensors, fan speeds and labels, nominal speeds, PWM-like fan control, and selected automatic/manual fan-control commands.

### Important APIs, types, and functions

Firmware calls use `struct smm_regs`, `struct dell_smm_ops`, and `dell_smm_call()`. Runtime state is `struct dell_smm_data`, including backend operations, fan multiplier/max values, discovered temperature/fan metadata, and nominal-speed tables. Key functions include `i8k_smm_func()`, `i8k_smm_call()`, `wmi_smm_call()`, `i8k_get_fan_status()`, `i8k_get_fan_speed()`, `i8k_get_fan_type()`, `i8k_get_fan_nominal_speed()`, `i8k_set_fan()`, `i8k_enable_fan_auto_mode()`, `i8k_get_temp()`, `dell_smm_is_visible()`, `dell_smm_read()`, `dell_smm_read_string()`, `dell_smm_write()`, and backend probe/init functions.

### Control flow

Module init applies DMI policy for blacklists, fan multiplier/max overrides, and automatic fan-control command whitelists. It then tries legacy SMM signature probing; if that fails, it registers the WMI driver. Legacy calls execute an SMM trap on CPU0 through `smp_call_on_cpu()`. WMI calls pack register values into the Dell WMI legacy-execute method and parse length-prefixed ACPI buffer results. Hwmon init probes up to ten temperature sensors and four fans, builds channel visibility from successful firmware calls, optionally registers thermal cooling devices, and allocates nominal-speed tables.

### State and persistence behavior

Temperature and fan RPM reads are live firmware calls, not cached. Fan type and nominal speeds are cached after probe. Fan state/PWM writes persist in BIOS/firmware until firmware or userspace changes them. Automatic fan control is write-only for some systems because the BIOS exposes no reliable readback. `/proc/i8k` state includes cached DMI BIOS version and machine ID.

### Dependencies and integration points

Dependencies include x86 SMM behavior, CPU hotplug locking, DMI, WMI/ACPI, procfs/i8k uapi when enabled, hwmon, thermal cooling devices, and module parameters. Integration points are `/sys/class/hwmon`, optional `/proc/i8k`, i8k ioctls, thermal zones bound to `dell-smm-fanN`, and Dell-specific DMI/WMI signatures.

### Risks

Firmware calls can be slow or unsafe on some machines; the file carries DMI blacklists for known fan bugs. Legacy calls must run on CPU0. Fan-control writes have safety impact, so the driver sets maximum fan speed when leaving automatic control without dedicated auto commands. Procfs can expose serial data unless restricted. WMI response parsing must reject malformed buffers.

### Test signals

Test DMI match/blacklist behavior, fallback from legacy to WMI, channel visibility on systems with different fan counts, slow-call warnings, fan multiplier autodetection, procfs ioctl permissions, thermal cooling get/set state, invalid PWM writes, and regression on blacklisted Dell models.
