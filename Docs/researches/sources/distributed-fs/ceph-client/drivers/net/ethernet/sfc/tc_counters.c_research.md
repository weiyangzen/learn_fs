# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_counters.c

Purpose: manages MAE counters used by SFC TC offload and receives firmware counter-update packets on a dedicated channel. It supports action-rule, conntrack, and outer-rule counter types.

Important APIs and functions: `efx_tc_init_counters()`, `efx_tc_destroy_counters()`, and `efx_tc_fini_counters()` manage counter-id and firmware-id rhashtables. `efx_tc_flower_allocate_counter()` allocates a firmware MAE counter and inserts it into `counter_ht`; `efx_tc_flower_release_counter()` removes it, frees firmware state, waits for RCU, flushes work, and frees memory. `efx_tc_flower_get_counter_index()` maps TC cookies to refcounted counter objects. `efx_tc_channel_type` describes the MAE counter RX channel.

Control flow: counter updates arrive through `efx_tc_rx()`, which decodes v1 or v2 packet formats, converts little-endian packed fields, validates identifiers, and calls `efx_tc_counter_update()`. Updates use a generation mark to ignore stale packets after firmware ID reuse, add packet/byte deltas, update `touched`, and schedule work. The work function walks action-set users and refreshes neighbour entries for encap actions that have seen traffic.

State and dependencies: persistent runtime state is in `efx->tc->counter_ht`, `counter_id_ht`, `seen_gen[]`, `flush_gen[]`, and wait queues. Each counter has a spinlock, generation, packet/byte totals, old user-reported totals, touched jiffies, work item, and user list. Dependencies include MAE firmware APIs, RX buffer handling, neighbour tables, and `mae_counter_format.h` packet layouts.

Risks and test signals: risks include firmware counter ID reuse, delayed packets racing with free, work item/list lifetime, malformed counter packet parsing, and CT one-bit counter semantics. Test with counter allocate/release loops, stats reads while deleting rules, v1/v2 update packets, flush wait wakeups, no extra interrupt vector path, and encap neighbour refresh after traffic.
