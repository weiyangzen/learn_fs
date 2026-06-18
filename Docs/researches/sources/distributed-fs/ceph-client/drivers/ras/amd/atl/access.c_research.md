# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/access.c

## Purpose
Provides serialized Data Fabric indirect register reads for AMD ATL. It abstracts FICAA/FICAD access, including legacy offsets and heterogeneous-node remapping.

## Important APIs, types, and functions
`df_indirect_mutex` serializes writes to the shared FICAA address register and reads from FICAD. `get_accessible_node()` maps logical node IDs to software-visible nodes on heterogeneous DF3.5 and DF4.5 systems. `__df_indirect_read()` performs the common read. Public internal helpers are `df_indirect_read_instance()` for instance-specific reads and `df_indirect_read_broadcast()` using instance ID `0xff`.

## Control flow
Callers pass node, function, register, instance ID, and result pointer. The code adjusts node visibility, bounds-checks against `amd_nb_num()`, fetches DF function 4 PCI device from `node_to_amd_nb(node)->link`, builds FICAA with optional instance enable, shifts register offset by two, chooses legacy or current FICAA/FICAD offsets from `df_cfg.flags.legacy_ficaa`, writes FICAA under mutex, then reads FICAD low.

## State and persistence
Only global state is the mutex and reads of `df_cfg`. Hardware-visible state is the transient FICAA selector write in PCI config space.

## Dependencies and integration
Depends on AMD northbridge helpers, PCI config accessors, `df_cfg` initialized by system discovery, and register field macros. Used by ATL system/map/UMC discovery code to read Data Fabric registers.

## Risks
Incorrect heterogeneous node mapping reads the wrong DF instance. FICAA/FICAD are shared registers, so missing mutex coverage would race; current function covers the pair. Only FICAD low is read, so future high-register users need extension. Bad `df_cfg.rev` or shift values can make node adjustment invalid.

## Test signals
Unit or hardware tests for legacy and current FICAA offsets, broadcast and instance reads, out-of-range nodes, missing DF function 4, heterogeneous DF3.5/DF4.5 mapping, and concurrent callers.
