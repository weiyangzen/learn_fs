# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/rl.c

## Purpose

`rl.c` provides two related services: generic firmware scheduling-element command wrappers used by QoS/eswitch code, and a lazy, refcounted packet-pacing rate-limit table used to share hardware rate-limit entries among consumers.

## Important APIs, Types, and Functions

Scheduling capability helpers are `mlx5_qos_tsar_type_supported()` and `mlx5_qos_element_type_supported()`. Firmware command wrappers are `mlx5_create_scheduling_element_cmd()`, `mlx5_modify_scheduling_element_cmd()`, and `mlx5_destroy_scheduling_element_cmd()`.

Rate-limit APIs are `mlx5_init_rl_table()`, `mlx5_cleanup_rl_table()`, `mlx5_rl_is_in_range()`, `mlx5_rl_are_equal()`, `mlx5_rl_add_rate()`, `mlx5_rl_remove_rate()`, `mlx5_rl_add_rate_raw()`, and `mlx5_rl_remove_rate_raw()`. The table is `dev->priv.rl_table`, with `rl_lock`, `max_size`, `min_rate`, `max_rate`, lazy `rl_entry[]`, and a table refcount. Each `mlx5_rl_entry` has a hardware index, raw context bytes, UID, dedicated flag, and per-entry refcount.

## Control Flow

Initialization checks QoS and packet pacing capabilities, initializes the mutex, and records table size/rate range from capabilities. The actual entry array is allocated lazily in `mlx5_rl_table_get()` on first rate addition and freed by `mlx5_rl_table_put()` when the table refcount falls to zero.

Adding a rate validates table support and range, locks `rl_lock`, allocates the table if needed, then calls `find_rl_entry()`. Shared entries reuse an existing non-dedicated entry with identical raw context and UID; dedicated entries take the first free slot. New entries are programmed with `SET_PP_RATE_LIMIT`, marked dedicated if requested, refcounted, and returned as a 1-based hardware index. Removal decrements the entry refcount and, when it reaches zero, sends `SET_PP_RATE_LIMIT` without context to clear the hardware entry. Cleanup clears every configured entry and frees the array.

## State and Persistence Behavior

Hardware state is the packet pacing rate-limit table, whose index 0 is reserved for unlimited rate and whose usable entries are represented as indexes 1..max_size. Driver state persists only while references exist unless cleanup forces clear. The table refcount tracks active users, while each entry refcount tracks consumers of identical or dedicated rates.

## Dependencies and Integration Points

The code depends on QoS capabilities, scheduling command layouts, packet pacing UID support, and the core command executor. It is integrated with QoS, flow/transport objects that need packet pacing, and exported symbol consumers.

## Risks and Edge Cases

`mlx5_rl_remove_rate_raw()` indexes `table->rl_entry[index - 1]` without local range checks, so callers must pass an index returned from add. `mlx5_rl_remove_rate()` calls `find_rl_entry()` without first ensuring `rl_entry` is non-NULL; it is safe only under the contract that remove follows a successful add while the table still exists. Lazy table refcounting must stay balanced across every add failure and remove path. Dedicated entries intentionally do not deduplicate, so capacity exhaustion is possible even with repeated identical rates.

## Test Signals

Test no-packet-pacing capability, invalid zero/out-of-range rates, shared duplicate add/remove refcounts, dedicated entry exhaustion, UID-capable and UID-less devices, cleanup with live entries, and fault injection for `SET_PP_RATE_LIMIT`. Observe firmware table clearing and that `max_size` excludes reserved index 0.
