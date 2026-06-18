# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-platform.c

## Purpose
This file parses firmware topology data for CoreSight devices and converts it into `coresight_platform_data` connection arrays. It supports Device Tree graph bindings, legacy DT bindings, and ACPI _DSD graph bindings, and provides CPU/static trace-id helpers.

## Important APIs, Types, And Functions
`coresight_add_out_conn()` appends a new output connection to a device, rejecting duplicate output ports except helper-style `src_port == -1`. `coresight_add_in_conn()` stores a reverse input reference on the destination device. `coresight_find_csdev_by_fwnode()` locates registered CoreSight devices by firmware node. OF parsing is centered on `of_coresight_parse_endpoint()` and `of_get_coresight_platform_data()`. ACPI parsing is centered on `_DSD` graph validation, `acpi_coresight_parse_link()`, and `acpi_coresight_parse_graph()`. Public helpers include `coresight_get_cpu()`, `coresight_get_static_trace_id()`, and `coresight_get_platform_data()`.

## Control Flow And State
For each output endpoint or ACPI master link, the parser resolves the remote endpoint/device, defers probing when the remote device is not yet present, stores a referenced destination fwnode, records source and destination port numbers, and optionally resolves a `filter-source` reference to a source device. Parsed connections are devm-managed under the local device and later completed by CoreSight registration/matching. ACPI input links are parsed only for direction validation and local input port awareness; output links produce actual `out_conns`.

## Dependencies And Integration Points
The file depends on OF graph APIs, ACPI object parsing, platform and AMBA bus lookup, `coresight-priv.h`, and `linux/coresight.h`. It is used by nearly every CoreSight component probe before `coresight_register()`. Remote fwnode references are released by platform-data cleanup outside this file.

## Risks And Test Signals
Topology parsing is probe-order sensitive; missing remote devices return `-EPROBE_DEFER`, while malformed graph data can abort a device probe. Duplicate output ports are rejected early. Reference ownership is subtle because destination fwnodes and bus devices are acquired during parsing and must be released on failure/unregister. Test signals include OF new and legacy bindings, ACPI graph packages with valid and invalid directions, disabled remote nodes, filter-source validation, duplicate ports, CPU phandle or ACPI parent CPU mapping, and static trace-id property reads.
