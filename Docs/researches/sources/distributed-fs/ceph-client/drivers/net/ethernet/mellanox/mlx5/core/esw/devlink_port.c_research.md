# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/devlink_port.c

Purpose: Creates, initializes, registers, unregisters, and describes devlink ports for mlx5 eswitch PF, VF, EC VF, and SF vports in offloads mode.

Important APIs/types/functions: PF/VF APIs are `mlx5_esw_offloads_pf_vf_devlink_port_init()` and cleanup. SF APIs are `mlx5_esw_offloads_sf_devlink_port_init()` and cleanup. Registration APIs are `mlx5_esw_offloads_devlink_port_register()`, unregister, and lookup. Static devlink ops expose port function attributes including HW address, RoCE, migratable, IPsec offload knobs under XFRM, max IO EQs, SF deletion, and state controls. PF registration may add a `max_SFs` devlink resource.

Control flow: Init allocates or attaches `struct mlx5_devlink_port`, populates switch ID and PCI PF/VF/SF attrs, stores it on the vport, and initializes mlx5 devlink port glue. Register selects ops by vport kind, computes the devlink port index, registers the port, creates a devlink rate leaf, and optionally registers PF resources. Unregister removes resources, detaches QoS parent, destroys the rate leaf, and unregisters the port.

State and persistence: State persists as `vport->dl_port` and in devlink's registered port/rate/resource objects. Adjacent vports alter VF attrs using `vport->adj_info`. Rate parent state is reset through QoS before devlink port teardown.

Dependencies and integration: Depends on devlink, mlx5 devlink helpers, eswitch vport type helpers, PCI identity, system image GUID, SF manager, XFRM offload callbacks, and QoS `mlx5_esw_qos_vport_update_parent()`.

Risks and test signals: Risks include wrong controller/PF/VF numbering for ECPF, external controller, EC VF, or adjacent vports; registration unwind if rate leaf creation fails; and stale QoS parent on unregister. Test signals include devlink port listing for PF/VF/SF/adjacent vports, devlink rate operations, PF max_SFs resource, XFRM function attributes, and clean unregister.
