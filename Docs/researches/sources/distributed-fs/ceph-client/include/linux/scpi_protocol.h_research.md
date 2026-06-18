# sources/distributed-fs/ceph-client/include/linux/scpi_protocol.h

Purpose: `scpi_protocol.h` exposes the older Arm System Control Processor Interface client API. It is a compact firmware-facing vtable for clocks, DVFS, sensors, and power-domain state before SCMI superseded much of this functionality.

Important APIs/types/functions: `struct scpi_opp` and `struct scpi_dvfs_info` describe frequency/voltage operating points and DVFS latency. `enum scpi_sensor_class` and `struct scpi_sensor_info` describe basic firmware sensors. `struct scpi_ops` carries function pointers for version lookup, clock range/value set/get, DVFS index and OPP-table handling, device-to-domain mapping, transition latency, OPP registration, sensor capability/info/value reads, and device power state get/set. `get_scpi_ops()` returns the active operations when `CONFIG_ARM_SCPI_PROTOCOL` is reachable and returns `NULL` otherwise.

Control flow: Consumers first call `get_scpi_ops()`, check for a non-NULL table, then call the relevant firmware operation. The header itself has no protocol state machine; the implementing SCPI driver owns transport messages and caching.

State and persistence behavior: SCPI operations can change firmware-controlled clock, DVFS, and power-domain state. The `scpi_dvfs_info` pointer returned by the implementation likely references implementation-owned OPP data, so consumers should treat it as read-only and scoped to the SCPI provider lifetime.

Dependencies and integration points: This integrates with `struct device`, OPP registration, clock users, sensor users, and platform firmware. It depends only on `<linux/types.h>` here but expects callers to include device declarations before using device-based callbacks.

Risks: The API predates SCMI and has a global `get_scpi_ops()` style, so absent-provider handling is essential. Packed firmware structs require exact layout. DVFS indexes must be validated against `count`, and callers must not assume every platform supports disabling a clock by writing zero.

Test signals: Boot with and without `CONFIG_ARM_SCPI_PROTOCOL`, validate `NULL` ops fallback, enumerate DVFS OPPs for device domains, test sensor count/info/value reads, and check that clock and power-state calls propagate firmware errors.
