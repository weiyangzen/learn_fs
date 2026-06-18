# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_domain.c

Purpose: owns SWS domain creation/destruction, capability discovery, vport capability caching, memory/send resources, checksum-recalculation helper table cache, modify-header pattern/argument resources, and peer-domain mapping.

Important APIs/functions: `mlx5dr_domain_create`, `mlx5dr_domain_destroy`, `mlx5dr_domain_is_support_ptrn_arg`, `mlx5dr_domain_get_recalc_cs_ft_addr`, `mlx5dr_domain_get_vport_cap`, and `mlx5dr_domain_set_peer`. Static helpers initialize caps, ICM pools, send ring, PD/UAR, vport caps, checksum table xarray, and modify-header resources.

Control flow: create allocates and initializes the domain, queries device/FDB capabilities, checks SW steering support for the requested domain type, sets max chunk sizes, allocates PD/UAR/memory pools/send ring/pattern-arg managers, initializes checksum table cache and debugfs, then returns. Destroy requires refcount 1, syncs steering, removes debugfs, destroys cached checksum FTs, send/memory resources, caps/xarrays, mutexes, and the domain.

State/persistence: domain state includes capabilities, RX/TX default/drop ICM addresses, vport cap xarray, definer xarray, peer-domain xarray, ICM pools, kmem caches, send ring, PD, UAR, pattern/argument managers, checksum-recalc FW table cache, debugfs state, and refcount. Firmware/device resources persist only for the domain lifetime.

Dependencies/integration: depends on command wrappers, ICM pool, send ring, STE context selection, FW helper tables, debug dump, eswitch/vport data, and mlx5 core PD/UAR APIs. Higher-level tables/rules/actions all hang from a domain.

Risks: partial init unwinding is complex and must mirror init order. `dr_domain_caps_uninit()` always clears FDB vport xarray, so caps init failure paths must ensure it was initialized. Cached vport and checksum helper entries can be created lazily and must not race teardown. Peer domain replacement adjusts refcounts under domain lock.

Test signals: create/destroy for NIC RX/TX/FDB across capability combinations, partial failure injection for each resource stage, vport cap lazy query and `-EBUSY` race, checksum FT cache creation, peer mapping refcount updates, and destroy while references remain.
