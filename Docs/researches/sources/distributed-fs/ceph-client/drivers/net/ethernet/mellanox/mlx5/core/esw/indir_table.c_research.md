# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/indir_table.c

Purpose: Implements an offloads indirection flow table used when uplink-to-VF/SF traffic needs source rewrite and optional decap recirculation before final vport forwarding.

Important APIs/types/functions: Public functions are `mlx5_esw_indir_table_init()`, destroy, `mlx5_esw_indir_table_needed()`, `mlx5_esw_indir_table_decap_vport()`, `mlx5_esw_indir_table_get()`, and put. Internal state includes `mlx5_esw_indir_table`, per-vport entries, and reference-counted recirculation rules with modify headers.

Control flow: `needed()` selects the indirection path for uplink ingress, VF/SF destination, same device, and source rewrite flag. `get()` locks the table, reuses or creates an entry by destination vport, increments forward refs or creates/references a decap recirculation rule, and returns the entry flow table. Entry creation builds an unmanaged FDB table at level 1 with recirc and fwd groups, optional recirc rule to chain table 0/1, and a fwd rule to the vport. `put()` decrements either forward ref or decap rule ref and destroys table, groups, rules, and entry when both references are gone.

State and persistence: State lives in `esw->fdb_table.offloads.indir`, its mutex, hash table, per-entry flow table/group/rule handles, `fwd_ref`, and recirc rule refcount/modify-header. Chain table references are acquired with `mlx5_chains_get_table()` and released on last recirc rule put.

Dependencies and integration: Depends on CLS_ACT, mlx5 chains, TC modify-header action builder, metadata register mapping, FDB namespace flow steering, tunnel decap attributes, source-port metadata helpers, and eswitch offload flow attributes.

Risks and test signals: Risks include asymmetric get/put for decap versus non-decap flows, chain table reference leaks, modify-header deallocation on failure, and hash key collisions if vport keying changes. Test signals include TC flows from uplink to VF/SF with source rewrite, decap recirculation, repeated add/delete sharing one destination vport, and no leaked unmanaged tables or chain refs.
