# sources/distributed-fs/ceph-client/drivers/hwmon/ltq-cputemp.c

Purpose: platform hwmon driver for the Lantiq VR9 v1.2 CPU temperature sensor.

Important APIs/types/functions: `ltq_cputemp_enable()` and `ltq_cputemp_disable()` manipulate `CGU_TEMP_PD` in `CGU_GPHY1_CR`. `ltq_read()` extracts the 9 bit temperature field and converts it to millidegrees. `ltq_hwmon_ops` exposes a single `temp1_input` plus chip thermal-zone registration.

Control flow: probe rejects non-VR9 v1.2 SoCs, registers a devm cleanup action to disable the sensor, enables it, then registers hwmon with info callbacks.

State and persistence behavior: no driver-private state. The driver toggles a SoC CGU bit for the device lifetime and clears it on cleanup.

Dependencies and integration points: depends on Lantiq SoC helpers from `<lantiq_soc.h>`, platform/OF matching, and hwmon thermal zone registration.

Risks: direct CGU register access is SoC-specific and probe is guarded only by `ltq_soc_type()`. The enable/disable bit name suggests power-down semantics, so hardware documentation is needed when changing polarity. No locking is used around CGU read-modify-write.

Test signals: build on Lantiq targets, probe rejection on other SoCs, register bit set/clear validation, and conversion tests for raw extremes covering -38 C to 154 C.
