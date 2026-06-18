## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-main.c

Purpose: this is the main Intel DFL FPGA Management Engine driver. It exposes FME header sysfs, char-device ioctls, thermal and power hwmon devices, global error sysfs, PR/perf feature integration, and DFL port assign/release operations.

Important APIs and functions: header sysfs exposes `ports_num`, `bitstream_id`, `bitstream_metadata`, `cache_size`, `fabric_version`, and `socket_id`. Header ioctls dispatch `DFL_FPGA_FME_PORT_RELEASE` and `DFL_FPGA_FME_PORT_ASSIGN` to DFL container helpers. Thermal init registers `dfl_fme_thermal` hwmon with temperature input, thresholds, alarms, and `temp1_max_policy` when throttling is supported. Power init registers `dfl_fme_power` hwmon with input, writable max/crit thresholds, alarms, and read-only Xeon/FPGA limits plus latency tolerance. The file operation layer supports API version, extension check, and subfeature ioctl dispatch.

Control flow: probe allocates `struct dfl_fme`, initializes enumerated subfeatures from `fme_feature_drvs`, then registers char-device ops. Subfeatures include header, PR management, global errors, thermal, power, and perf. Open/release use DFL use counting and clear IRQ triggers on final close. Remove unregisters ops, uninitializes features, and clears private data.

State and persistence: FME private data tracks PR-created manager/region/bridge lists through `struct dfl_fme`. HWMON readings and thresholds are direct hardware register accesses; power threshold writes persist in FME registers. Use count and IRQ triggers are maintained by DFL common data.

Dependencies and integration: it depends on DFL core infrastructure, hwmon, perf feature declarations, FPGA PR helpers, global error helpers, and Linux units conversion. It is the parent feature driver that wires together FME-specific subfeature files.

Risks: `FPGA_DFL_FME` depends on both hwmon and perf even if deployments do not use monitoring. Power threshold writes clamp from microwatts to watts with `PWR_THRESHOLD_MAX`, which can surprise users expecting exact values. Thermal visibility depends on hardware throttle capability. Subfeature ioctl dispatch returns `-EINVAL` if no subfeature handles a command, while subfeatures use `-ENODEV` as "not mine".

Test signals: test header sysfs against known capability registers, port assign/release ioctls, hwmon registration and unit conversions, writable power thresholds, final-close IRQ cleanup, subfeature init failure unwinds, and module removal after PR/perf/error initialization.
