# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/devlink.c

Purpose: exposes mv88e6xxx switch internals through DSA devlink parameters, resources, regions, and fixed ASIC information. It turns hardware ATU/VTU/STU/PVT/register state into low-level debug snapshots and exposes ATU hash selection where supported.

Important APIs/types/functions: `mv88e6xxx_devlink_param_get/set()`, `mv88e6xxx_setup_devlink_params()`, `mv88e6xxx_setup_devlink_resources()`, `mv88e6xxx_setup_devlink_regions_global()`, `mv88e6xxx_setup_devlink_regions_port()`, and `mv88e6xxx_devlink_info_get()` are the DSA-facing entry points. Snapshot helpers allocate raw arrays for global registers, per-port registers, ATU entries, VTU entries, STU entries, and PVT entries.

Control flow: setup registers one runtime driver parameter, an ATU resource tree with per-bin occupancy callbacks, and conditional global devlink regions. Snapshot callbacks lock the chip register bus, walk hardware operation interfaces, copy register values into allocated buffers, then hand those buffers to devlink with `kfree` destructors.

State and persistence: it does not own persistent state; it observes switch tables, PVT mapping, and registers that persist in hardware until reset or reconfiguration. Runtime state is stored in `chip->regions[]` and `chip->ports[port].region`.

Dependencies/integration: depends on DSA devlink wrappers, Global1/Global2 ATU/VTU/PVT helpers, port register access, `chip->fid_bitmap`, and capability helpers such as `mv88e6xxx_has_stu()`.

Risks: ATU region sizing uses `mv88e6xxx_num_databases()` but may hold more than one MAC per FID, so the snapshot buffer can be undersized if many entries exist in a database. Error paths must avoid leaking allocated snapshots while register lock is held. Snapshots are raw, generation-specific ABI-like debug data.

Test signals: `devlink resource show` should report ATU occupancy, `devlink region dump` should work for global/port/ATU/VTU/STU/PVT where supported, unsupported hash ops should return `-EOPNOTSUPP`, and teardown should destroy only created regions.
