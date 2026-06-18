# sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra194-bpmp-thermal.h

Source read summary: 16 lines, 448 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/thermal/tegra194-bpmp-thermal.h` declares thermal binding constants for the thermal-zone, including sensor or thermal-zone indexes, throttling levels, trimming modes, or no-limit sentinel values.

Important APIs, types, and functions: The file exports 6 visible constants or packing macros; representative names are `TEGRA194_BPMP_THERMAL_ZONE_CPU`, `TEGRA194_BPMP_THERMAL_ZONE_GPU`, `TEGRA194_BPMP_THERMAL_ZONE_AUX`, `TEGRA194_BPMP_THERMAL_ZONE_PLLX`, `TEGRA194_BPMP_THERMAL_ZONE_AO`, `TEGRA194_BPMP_THERMAL_ZONE_TJ_MAX`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Thermal-zone nodes include these values in `thermal-sensors`, trip, cooling, or calibration properties; thermal drivers map the IDs to hardware sensors or firmware BPMP zones.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Sensor-index drift can apply trips to the wrong thermal domain, while invalid throttling or trimming values can either overthrottle or fail to protect hardware.

Test signals: Build DTS users, validate dt-schema constraints, compare indexes with thermal driver tables, and run thermal-zone readout plus trip/cooling-device tests.
