# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti-platform.c

## Purpose
`coresight-cti-platform.c` parses firmware data for CTI devices and builds the trigger-connection metadata consumed by the CTI core and sysfs layers.

## Important APIs, Types, And Functions
The file defines DT property names such as `trig-conns`, `arm,cs-dev-assoc`, trigger signal/type arrays, filters, connection names, and CTM ID. `cti_plat_get_cpu_at_node()` resolves CPU affinity. `cti_plat_get_node_name()` and `cti_plat_get_csdev_or_node_name()` produce association names and optional `coresight_device` pointers. `cti_plat_create_v8_connections()` builds architecturally-defined PE and optional ETM connections. `cti_plat_create_connection()` parses implementation-defined child connection nodes. `coresight_cti_get_platform_data()` returns a minimal CoreSight platform-data object after populating CTI-specific metadata in `drvdata`.

## Control Flow
During CTI probe, `coresight_cti_get_platform_data()` allocates zeroed platform data and calls `cti_plat_get_hw_data()`. That reads `arm,cti-ctm-id`, chooses v8 architectural parsing if compatible, otherwise walks child nodes named `trig-conns`, and falls back to a default all-trigger connection if no explicit connections were found. Each parsed connection allocates input/output trigger groups, reads signal indexes and optional signal types, applies filter signals, resolves CPU or CoreSight device association, and appends the connection to `drvdata->ctidev.trig_cons`.

## State And Persistence
The parser mutates `drvdata->ctidev` and `drvdata->config`: CPU affinity, CTM ID, trigger connection list, trigger-use masks, and output filters. The returned `coresight_platform_data` is intentionally mostly empty because CTI does not use normal trace-path input/output topology for data flow.

## Dependencies And Integration Points
The file depends on generic firmware property APIs, OF helpers, DT binding constants in `dt-bindings/arm/coresight-cti-dt.h`, and CTI core allocation/connection APIs. It integrates firmware declarations with CTI sysfs dynamic groups and association fixup in the core.

## Risks
Signal count and type arrays must agree with hardware `nr_trig_max`; inconsistent firmware returns `-EINVAL`. `cti_plat_read_trig_group()` builds masks from supplied signal indexes but does not explicitly check each index against `nr_trig_max` in that function, relying on count checks and later usage. Association by node name is fragile when device registration ordering or firmware naming differs. The v8 architectural defaults hard-code signal masks and types, so binding compatibility must be accurate.

## Test Signals
DT parsing tests should cover v8 architectural CTIs with CPU and ETM association, implementation-defined connections with signal/type/filter arrays, missing CPU errors, fallback default connections, invalid oversized arrays, and association when referenced CoreSight devices register before or after the CTI.
