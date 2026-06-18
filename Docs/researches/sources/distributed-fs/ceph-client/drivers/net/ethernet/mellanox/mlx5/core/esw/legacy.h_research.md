# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/legacy.h

Purpose: Declares legacy eswitch lifecycle, vport ACL, and drop-stat APIs.

Important APIs/types/functions: Exposes `esw_legacy_enable()`, `esw_legacy_disable()`, `esw_legacy_vport_acl_setup()`, `esw_legacy_vport_acl_cleanup()`, and `mlx5_esw_query_vport_drop_stats()`. It also defines the legacy SR-IOV vport event mask for UC, MC, and promiscuous changes.

Control flow and integration: `eswitch.c` and related vport lifecycle code use this interface when entering/leaving legacy mode or enabling/disabling individual vports. ACL setup/cleanup connect legacy mode to ACL implementation files.

State and persistence: No state is stored here. Declared functions mutate eswitch legacy FDB state and per-vport ACL/counter state.

Risks and test signals: Risks are duplicated event-mask definitions drifting from implementation and API drift with `legacy.c`. Test signals include compile coverage and legacy mode transitions with correct event subscriptions.
