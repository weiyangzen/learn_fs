# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/vport.c

Purpose: provides HWS vport GVMI lookup and caching for eswitch-manager contexts.

Important APIs/functions: `mlx5hws_vport_init_vports`, `mlx5hws_vport_uninit_vports`, and `mlx5hws_vport_get_gvmi`. Static helpers add a queried GVMI to an xarray and detect whether a vport is the eswitch manager PF/ECPF.

Control flow: initialization is a no-op outside eswitch manager mode; otherwise it initializes `vport_gvmi_xa`, queries the manager GVMI, and records uplink GVMI as zero. Lookup returns cached manager/uplink values for special vports or lazily queries other vports via `mlx5hws_cmd_query_gvmi`, inserts an `xa_mk_value`, and reloads to handle races/`-EBUSY`.

State/persistence: state is `ctx->vports.vport_gvmi_xa`, `esw_manager_gvmi`, and `uplink_gvmi`. It caches firmware query results in memory until context uninit destroys the xarray.

Dependencies/integration: depends on HWS command GVMI query, context capability flags (`eswitch_manager`, `is_ecpf`), mlx5 vport constants, and Linux xarray APIs. Consumers are vport/action paths needing hardware GVMI values.

Risks: no explicit locking surrounds xarray lookup/insert; the code tolerates insert races with reload, but callers must not use after uninit. Query failures are normalized to `-EINVAL` in the add path, losing original firmware error detail.

Test signals: manager PF and ECPF lookups, uplink lookup, dynamic VF/SF lookup, concurrent first lookup of one vport, non-eswitch-manager rejection, and teardown after cached entries.
