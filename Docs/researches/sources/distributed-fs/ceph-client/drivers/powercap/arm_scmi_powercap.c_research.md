# sources/distributed-fs/ceph-client/drivers/powercap/arm_scmi_powercap.c

## Purpose
`arm_scmi_powercap.c` bridges ARM SCMI Powercap protocol domains into the generic Linux powercap sysfs framework. It registers SCMI firmware-advertised powercap domains as hierarchical powercap zones with one constraint each.

## Important APIs, Types, And Functions
`struct scmi_powercap_zone` wraps SCMI domain info, protocol handle, powercap zone, tree state, and list node. `struct scmi_powercap_root` stores all zones and height-indexed registered lists. Zone callbacks implement measurement, enable get/set, cap get/set, PAI time-window get/set, and min/max reporting through `scmi_powercap_proto_ops`. `scmi_powercap_normalize_cap()` and `_time()` clamp/round user requests to firmware limits. `scmi_zones_register()` registers parent zones before children and tracks heights for reverse unregister.

## Control Flow
Module init registers a powercap control type named `arm-scmi`, then registers an SCMI driver. Probe gets the SCMI Powercap protocol, reads domain count, allocates zone arrays, fetches each domain's info, marks domains with unsupported abstract scale invalid, and calls `scmi_zones_register()`. Registration walks domain relationships, recursing upward through parents before registering a child. Remove unregisters zones from leaves to roots. Module exit unregisters the SCMI driver and control type.

## State, Persistence, And Dependencies
State is the global control type, global protocol-ops pointer, per-device root arrays, per-zone flags, and firmware-backed caps/PAI/enables. No nonvolatile kernel state is persisted; all constraints are forwarded to SCMI firmware. Dependencies include the SCMI core/protocol handle and powercap framework.

## Integration Points
The SCMI id table binds protocol `SCMI_PROTOCOL_POWERCAP` with name `"powercap"`. Each registered zone is named from SCMI domain info and uses the SCMI parent id to build the sysfs hierarchy. Unsupported abstract-scale leaf domains are pruned; unsupported internal domains abort registration.

## Risks
`powercap_ops` is file-global, so multiple SCMI instances with different protocol-op pointers would share it. `scmi_powercap_register_zone()` removes invalid zones from the list but non-leaf invalid zones fail later; hierarchy assumptions rely on protocol validation. `scmi_powercap_get_max_power_range_uw()` returns `U32_MAX` independent of scaling/range. Cap normalization rounds down after clamping; requests just above minimum may round below the minimum if `min_power_cap` is not aligned to `power_cap_step`.

## Test Signals
Test domain trees out of order, multiple root domains, unsupported abstract-scale leaves and internal nodes, cap/time normalization, monitoring-disabled domains, cap/pai config-disabled domains, enable get/set, remove unregister order, SCMI protocol errors, and multiple SCMI device instances if supported.
