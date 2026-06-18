# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/ingress_ofld.c

Purpose: Programs switchdev/offload-mode ingress ACL rules. Its job is to tag packets with vport metadata for source-port matching, push priority VLAN tags for VF prio-tag mode, and optionally install an uplink source-port drop rule used by LAG-related paths.

Important APIs/types/functions: Public entry points are `esw_acl_ingress_ofld_setup()`, `esw_acl_ingress_ofld_cleanup()`, `mlx5_esw_acl_ingress_vport_metadata_update()`, `mlx5_esw_acl_ingress_vport_drop_rule_create()`, and `mlx5_esw_acl_ingress_vport_drop_rule_destroy()`. Internal pieces allocate modify-header actions for `metadata_reg_c_0`, create priority-tag allow rules, create drop groups, and manage metadata/prio/drop flow groups.

Control flow: `esw_acl_ingress_ofld_setup()` is a no-op unless metadata matching or prio-tag is required. The internal setup path counts required FTEs, creates the ingress ACL table, creates groups in deterministic order, and then installs metadata and prio-tag rules. Metadata updates destroy existing rules, update `vport->metadata`, and recreate rules, rolling the metadata value back to `default_metadata` on failure. Drop-rule create lazily creates the ACL if missing and cleans it up only if this call created it.

State and persistence: State is stored in `vport->ingress.acl`, common `allow_rule`, and `vport->ingress.offloads` members for modify headers, metadata/prio/drop groups, and drop rule. `vport->metadata` is persistent vport state used by subsequent match construction.

Dependencies and integration: Relies on mlx5 metadata match/set helpers, firmware capabilities `prio_tag_required`, vport type helpers, flow steering, modify-header allocation, and common ACL cleanup. Consumers include offloads mode vport setup, metadata refresh paths, and LAG/uplink drop handling.

Risks and test signals: Key risks are incorrect FTE sizing when capabilities combine, stale modify headers on metadata updates, and cleanup of lazily-created uplink ACLs. Test signals include switchdev VF traffic with metadata matching, prio-tag-required firmware, vport metadata rewrite, LAG drop rule create/destroy, and repeated setup/cleanup without flow object leaks.
