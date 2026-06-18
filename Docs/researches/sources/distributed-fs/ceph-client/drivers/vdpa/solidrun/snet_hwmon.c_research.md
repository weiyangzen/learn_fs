<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_hwmon.c

Purpose: Registers an optional hwmon device for SolidRun DPU telemetry exposed through BAR registers.

Important APIs/functions: `psnet_create_hwmon()` registers a hwmon device with `devm_hwmon_device_register_with_info()`. `snet_howmon_read()` maps hwmon attributes to BAR offsets for voltage, power, current, and two temperature channels. `snet_hwmon_read_string()` provides labels.

Control flow: If PF config flags request hwmon and `CONFIG_HWMON` is enabled, `snet_main.c` calls `psnet_create_hwmon()` after SR-IOV setup. Sysfs hwmon reads call into the ops table, which uses `psnet_read64()` at `cfg.hwmon_off + offset`.

State and persistence: No persistent state. `psnet->hwmon_name` stores the registered name. Sensor readings are live MMIO values.

Dependencies and integration points: Depends on Linux hwmon framework and `struct psnet` from `snet_vdpa.h`. Uses register offsets agreed with DPU firmware.

Risks: All attributes are exposed read-only as visible, while unsupported type/attribute/channel combinations return `-EOPNOTSUPP`. The function names contain `howmon`/`hwmono` typos but are internally consistent. Units and scaling are assumed to already match hwmon expectations from firmware.

Test signals: With device hwmon flag set, verify `/sys/class/hwmon` entry named `snet_<pci>` and readable labels/values for temp, power, current, and voltage. Exercise unsupported temp channel max and failure to register as non-fatal warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/solidrun/snet_hwmon.c -->
