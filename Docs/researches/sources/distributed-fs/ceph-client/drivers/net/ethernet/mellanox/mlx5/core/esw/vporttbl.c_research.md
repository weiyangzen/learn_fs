# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/vporttbl.c

## Purpose
Implements reference-counted per-vport FDB table caching for eswitch offloads. TC split/mirror forwarding paths request a flow table keyed by chain, priority, vport, local VHCA ID, and namespace attributes; the module creates the table on first use and destroys it after the last rule releases it.

## Important APIs, Types, and Functions
`struct mlx5_vport_key` is a packed hash key containing `chain`, `prio`, `vport`, `vhca_id`, and `vport_ns`. `struct mlx5_vport_table` stores the hash node, `struct mlx5_flow_table *fdb`, rule reference count, and key. `mlx5_esw_vporttbl_get()` is the public acquire path; `mlx5_esw_vporttbl_put()` is the public release path. Internal helpers initialize namespace flags from the eswitch encap mode, create auto-grouped flow tables, hash flow attrs into keys, and look up entries under the vports table mutex.

## Control Flow and State
`mlx5_esw_vporttbl_get()` locks `esw->fdb_table.offloads.vports.lock`, mutates the caller-provided namespace flags for tunnel reformat/decap when encap is enabled, computes a `jhash()` over the packed key, and searches `esw->fdb_table.offloads.vports.table`. A hit increments `num_rules`; a miss allocates an entry, obtains the FDB namespace, creates an auto-grouped FDB table with priority `FDB_PER_VPORT`, sets `num_rules = 1`, and inserts the entry in the hash. `mlx5_esw_vporttbl_put()` recomputes the same key, decrements `num_rules`, and on zero removes the hash entry, destroys the flow table, and frees the cache node.

## Dependencies and Integration Points
Depends on `eswitch.h` for `struct esw_vport_tbl_namespace`, `struct mlx5_vport_tbl_attr`, eswitch state, and warning helpers. It integrates with `eswitch_offloads.c` through `mlx5_esw_vporttbl_get/put()` in split offloaded rule handling and in pre-opening per-vport level-1 tables when chain priorities are unsupported. It also depends on flow steering APIs `mlx5_get_flow_namespace()`, `mlx5_create_auto_grouped_flow_table()`, and `mlx5_destroy_flow_table()`.

## Risks and Test Signals
The caller-owned `vport_ns->flags` object is modified on every get/put, so shared namespace instances must tolerate idempotent flag widening when encap is enabled. Correctness depends on always balancing get/put for split and forwarding rules; a missing put leaks flow tables, while an extra put can destroy a table still referenced by hardware rules. The packed key avoids padding instability, but any future field addition must preserve hash and memcmp behavior. Test signals include TC split flow add/delete loops, encap mode toggles, failure injection around table creation, hash collision coverage, and leak checks after eswitch offloads disable.
