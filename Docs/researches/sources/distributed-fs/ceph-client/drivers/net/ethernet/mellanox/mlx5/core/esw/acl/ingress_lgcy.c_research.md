# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/acl/ingress_lgcy.c

Purpose: Implements legacy-mode ingress ACL programming for non-manager vports. It enforces spoof-check and VST VLAN behavior by allowing a matched ingress packet and optionally dropping all unmatched packets with a drop counter.

Important APIs/types/functions: `esw_acl_ingress_lgcy_setup()` is the main setup path, and `esw_acl_ingress_lgcy_cleanup()` tears down rules, groups, table, and drop counter. Internal helpers create four ordered groups: untagged+SMAC spoof-check, untagged-only, spoof-check-only, and drop. `esw_acl_ingress_lgcy_rules_destroy()` removes per-vport allow/drop rules.

Control flow: Setup first destroys existing legacy ingress rules, creates or reuses a drop flow counter when supported, and exits through cleanup if VLAN, QoS, and spoof-check are all disabled. It lazily creates an ingress ACL table with four FTEs and the four groups, builds a flow spec matching VLAN tag and/or source MAC, adds an allow rule, and adds a drop rule only when a VLAN check or spoof-check requires a deny fallback. On error it calls full cleanup, so partially-created groups and counters are not left active.

State and persistence: State lives in `vport->ingress.acl`, `vport->ingress.allow_rule`, `vport->ingress.legacy.drop_rule`, legacy group pointers, and `drop_counter`. The counter persists across rule recreation until final cleanup, allowing drop stats to be queried by legacy code.

Dependencies and integration: Uses mlx5 flow steering APIs, `esw_vst_mode_is_steering()`, firmware capabilities such as `flow_counter` and `vport_cvlan_insert_always`, Ethernet MAC helpers, and the common ACL helper functions. It is invoked by `esw_legacy_vport_acl_setup()` and by legacy configuration changes such as spoof-check updates.

Risks and test signals: Risk centers on group ordering, VLAN mode differences, missing counter support, and rollback correctness. Regressions show as spoof-check bypass, VLAN-tag acceptance/rejection errors, unexpected ingress drops, or leaked ACL objects during vport disable. Useful tests include legacy SR-IOV with VST VLAN, QoS-only VLAN tag insertion, spoof-check enable/disable with invalid MAC, and drop counter queries.
