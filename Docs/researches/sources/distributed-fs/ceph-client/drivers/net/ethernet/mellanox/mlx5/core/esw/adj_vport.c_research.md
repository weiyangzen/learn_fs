# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/adj_vport.c

Purpose: Creates, registers, and destroys adjacent E-Switch vports for delegated VHCAs. These synthetic/adjacent vports let the local eswitch manage representors and ACL namespaces for functions owned by another VHCA.

Important APIs/types/functions: `mlx5_esw_adjacent_vhcas_setup()` queries delegated VHCA records and creates adjacent vports. `mlx5_esw_adjacent_vhcas_cleanup()` destroys all adjacent VF vports. `mlx5_esw_adj_vport_modify()` sends `MODIFY_VPORT_STATE` to connect/disconnect ingress and egress. Internal helpers wrap firmware `CREATE_ESW_VPORT` and `DESTROY_ESW_VPORT`, allocate/free `struct mlx5_vport`, add/remove ACL namespaces, and add/remove offload representors.

Control flow: Setup checks `delegated_vhca_max`, allocates a query output buffer, issues `QUERY_DELEGATED_VHCA`, and iterates returned function RID records. Each vport create calls firmware, allocates eswitch vport metadata, marks the xarray entry as VF, stores adjacency identity and parent PCI/function IDs, creates ACL namespaces, and adds the offloads representor. Failure unwinds namespaces, vport allocation, and firmware vport creation. Cleanup scans VF vports and destroys those with `vport->adjacent`.

State and persistence: State persists in `esw->vports`, `esw->last_vport_idx`, `vport->adjacent`, `vport->vhca_id`, and `vport->adj_info`. Firmware also has created ESW vport objects. Destruction decrements `last_vport_idx`, which assumes adjacent vport count changes in stack order.

Dependencies and integration: Integrates with firmware commands, xarray vport storage, ACL namespace management in flow steering, offloads representor add/remove, and devlink port attribute handling that reads `vport->adj_info`.

Risks and test signals: Risks include partial setup leaks, stale `last_vport_idx` if adjacent vports become non-LIFO, and failure to remove ACL namespaces before destroying firmware vports. Test signals include delegated VHCA enumeration, representor creation for adjacent functions, devlink PF/VF numbering for adjacent vports, repeated setup/cleanup, and vport state connect/disconnect command success.
