# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_qdisc.c

Work item: `subset-b-004562`

## Purpose

`spectrum_qdisc.c` implements Mellanox Spectrum switchdev offload for Linux traffic-control qdiscs on a Spectrum port. It receives `ndo_setup_tc()` qdisc and qevent requests for RED, PRIO, ETS, TBF, and FIFO qdiscs, validates whether the requested qdisc tree is representable by the ASIC, programs the relevant hardware queueing registers through mlxsw port helpers, and translates periodic hardware counters back into tc statistics.

The file owns a per-port software shadow tree rooted at `mlxsw_sp_port->qdisc->root_qdisc`. That tree is the driver's source of truth for which qdisc handles are currently offloaded, how tc classes map to Spectrum traffic classes, which invisible FIFO children have been observed, and what counter baselines should be subtracted when tc asks for stats.

## Important APIs, Types, and Data

- `enum mlxsw_sp_qdisc_type` distinguishes supported internal qdisc kinds: none, RED, PRIO, ETS, TBF, and FIFO.
- `struct mlxsw_sp_qdisc_ops` is the internal polymorphic interface for qdisc-specific behavior. It provides parameter validation, hardware replace/destroy, stats and xstats collection, stats cleanup, unoffload handling, class lookup, child count, and parent-derived priority/traffic-class mapping callbacks.
- `struct mlxsw_sp_qdisc` is a node in the offloaded qdisc tree. It stores the tc handle, ops pointer, parent pointer, child array, class count, per-node stats baselines, RED xstats baselines, and ETS-specific band metadata.
- `struct mlxsw_sp_qdisc_state` is allocated per port by `mlxsw_sp_tc_qdisc_init()`. It contains the root qdisc, a `future_handle`/`future_fifos[]` cache for invisible FIFO notifications that arrive before their classful parent is known, and a mutex protecting qdisc state.
- `struct mlxsw_sp_qdisc_ets_data` and `struct mlxsw_sp_qdisc_ets_band` track, per PRIO/ETS band, the software priority bitmap and hardware traffic class number.
- `struct mlxsw_sp_qevent_block` and `struct mlxsw_sp_qevent_binding` manage tc qevent flow blocks for RED early-drop and ECN-mark events. They connect matchall mirror/trap actions to Spectrum SPAN triggers.

The exported entry points declared in `spectrum.h` are:

- `mlxsw_sp_tc_qdisc_init()` / `mlxsw_sp_tc_qdisc_fini()` for port lifetime.
- `mlxsw_sp_setup_tc_red()`, `mlxsw_sp_setup_tc_prio()`, `mlxsw_sp_setup_tc_ets()`, `mlxsw_sp_setup_tc_tbf()`, and `mlxsw_sp_setup_tc_fifo()` for qdisc offload commands.
- `mlxsw_sp_setup_tc_block_qevent_early_drop()` and `mlxsw_sp_setup_tc_block_qevent_mark()` for RED qevent block binding.

## Generic Qdisc Tree Flow

All qdisc setup functions lock `mlxsw_sp_port->qdisc->lock`, delegate to an unlocked helper, and unlock before returning. The helpers first locate the target tree node with `mlxsw_sp_qdisc_find()`, using `TC_H_ROOT` for the root and `ops->find_class()` for classful children.

`mlxsw_sp_qdisc_replace()` is the common replace path. If a different qdisc type already occupies a node, it destroys that node first. Creation runs `ops->check_params()`, allocates child qdisc nodes when needed, switches root headroom mode to tc mode, installs `ops`/`handle`/`num_classes`, validates the whole tree with `mlxsw_sp_qdisc_tree_validate()`, and calls the type-specific `replace()` callback to program hardware. On failure it clears the software node, frees children, and restores the previous headroom state.

`mlxsw_sp_qdisc_change()` is used when the same qdisc type is reconfigured. It validates parameters, calls the type-specific `replace()`, cleans stats if the handle changed, then updates the handle. If validation or hardware programming fails, the qdisc is optionally unoffloaded via `ops->unoffload()` and then destroyed.

`mlxsw_sp_qdisc_destroy()` recursively destroys child qdiscs, subtracts the destroyed node backlog from its ancestors, calls qdisc-specific destroy and stats cleanup callbacks, clears the node, and frees its child array. When destroying the root node, it resets port headroom back to DCB mode before clearing the qdisc.

The tree validator enforces Spectrum-supported compositions:

- RED cannot be nested under another RED, cannot have ETS/PRIO beneath it, and prevents a root TBF below it.
- TBF may appear as a root shaper or as a per-traffic-class shaper, but only one TC-level TBF is allowed in a path.
- PRIO and ETS cannot be nested below RED or another ETS/PRIO.
- FIFO is always accepted as a leaf.

## Qdisc-Specific Behavior

### RED

`mlxsw_sp_qdisc_ops_red` models RED as one classful qdisc with a single child. `mlxsw_sp_qdisc_red_check_params()` rejects invalid thresholds, zero thresholds, and maximum thresholds beyond the guaranteed shared buffer resource. `mlxsw_sp_qdisc_red_replace()` retroactively creates any cached invisible FIFO child, converts RED thresholds from bytes to cells, converts probability to a percentage, and programs congestion with `mlxsw_sp_tclass_congestion_enable()`. Destroy disables the congestion profile for the relevant traffic class.

RED stats combine bstats from priorities mapped to the qdisc and queue stats from WRED drops, ECN marks, tail drops, and backlog. RED xstats keep independent baselines for `prob_drop`, `prob_mark`, and `pdrop`, so subsequent tc reads receive deltas from hardware counters.

### TBF

`mlxsw_sp_qdisc_ops_tbf` also has one child. Root TBF maps to the port hierarchy level, while non-root TBF maps to the subgroup hierarchy so both unicast and multicast traffic are shaped together. Parameter validation converts byte-per-second tc rates to kbps, rejects values at or above `MLXSW_REG_QEEC_MAS_DIS`, and requires burst sizes to be a power-of-two multiple of 64 bytes within ASIC-supported burst-size limits. Replace programs `mlxsw_sp_port_ets_maxrate_set()` with the selected hierarchy, traffic class, rate, and burst size; destroy disables the max-rate shaper.

### FIFO

`mlxsw_sp_qdisc_ops_fifo` has no hardware programming callback beyond accepting the replace. Its main role is to represent invisible leaf qdiscs and provide stats. `mlxsw_sp_qdisc_future_fifo_replace()` and `mlxsw_sp_qdisc_future_fifos_init()` handle Linux notification ordering where FIFO children for a not-yet-known PRIO/ETS/RED/TBF parent arrive first. `__mlxsw_sp_setup_tc_fifo()` caches such notifications by parent major handle and band until the parent qdisc replace path can attach them.

### PRIO and ETS

PRIO and ETS share the implementation in `__mlxsw_sp_qdisc_ets_replace()`. Both allocate `ets_data` lazily and assign Spectrum traffic classes in reverse band order via `MLXSW_SP_PRIO_BAND_TO_TCLASS()`. For each active band, the driver programs scheduler parameters with `mlxsw_sp_port_ets_set()`, updates priority-to-traffic-class mapping with `mlxsw_sp_port_prio_tc_set()`, recalculates the priority bitmap, rebases stats when the bitmap changes, and attaches any cached invisible FIFO child. Inactive bands have child qdiscs destroyed, priority bitmap cleared, and scheduler configuration disabled.

PRIO passes zero quanta and weights, while ETS uses tc-provided `quanta`, `weights`, and `priomap`. Both enforce `bands <= IEEE_8021QAZ_MAX_TCS`. Their class lookup maps tc class minor IDs to zero-based band indices. Their stats aggregate all child traffic-class counters and keep parent baselines.

`__mlxsw_sp_qdisc_ets_destroy()` resets each priority to the default traffic class, disables subgroup ETS scheduling, frees `ets_data`, and clears the pointer.

## Graft and Notification Ordering

Linux permits linking qdiscs to arbitrary classes, and qdisc replace notifications can arrive before parent graft notifications. The driver uses `mlxsw_sp_qdisc_graft()` to verify that a child qdisc actually ended up under the class implied by the parent handle used during replace. If a graft points at a qdisc already offloaded elsewhere, the existing offload is destroyed. If the grafted handle does not match the expected child slot, the target slot is destroyed and the operation returns `-EOPNOTSUPP`, forcing software fallback for ambiguous or unsupported sharing.

Invisible FIFO grafts with `child_handle == 0` are ignored because they are expected to be followed by the original qdisc destroy.

## Stats and Persistence Behavior

The driver does not persist qdisc configuration across port teardown. `mlxsw_sp_tc_qdisc_init()` allocates in-memory per-port state, and `mlxsw_sp_tc_qdisc_fini()` destroys the mutex and frees it. Hardware state is expected to be unwound by qdisc destroy paths and broader port teardown before final free.

Stats are persistent only as in-memory baselines inside `struct mlxsw_sp_qdisc`. Hardware counters are read from `mlxsw_sp_port->periodic_hw_stats.xstats` and `stats`. `mlxsw_sp_qdisc_update_stats()` subtracts per-qdisc baselines, reports deltas into tc bstats/qstats, converts backlog cells to bytes, and then advances the baseline. Clean-stat callbacks rebase counters on qdisc creation, handle changes, unoffload, and priority remapping.

Backlog is tracked carefully because parent qdiscs aggregate child backlog. Destroy subtracts a node's backlog from ancestors, and unoffload paths subtract offloaded backlog from tc-provided software qstats to avoid double-counting when a qdisc falls back to software.

## Qevent Flow

The qevent section offloads RED early-drop and mark blocks. `spectrum.c` routes `FLOW_BLOCK_BINDER_TYPE_RED_EARLY_DROP` to `mlxsw_sp_setup_tc_block_qevent_early_drop()` and `FLOW_BLOCK_BINDER_TYPE_RED_MARK` to `mlxsw_sp_setup_tc_block_qevent_mark()`.

Binding looks up or creates a shared `flow_block_cb` backed by `struct mlxsw_sp_qevent_block`, finds the offloaded qdisc by `f->sch->handle`, derives its traffic class, creates a binding for the requested SPAN trigger, configures existing matchall entries, and registers the callback if this is the first binding. Unbind removes the binding, deconfigures SPAN state, destroys the binding, and removes the flow block callback when its refcount reaches zero.

Only one matchall filter is supported per qevent block. It must be chain 0, protocol `ETH_P_ALL`, have exactly one action, and disable hardware counters. Early-drop supports mirror and trap actions; ECN mark supports mirror only. Mirror actions create regular SPAN sessions to the target netdev. Trap actions use the buffer-drop devlink trap group policer and the buffer SPAN session. Both paths enable the per-port, per-traffic-class SPAN trigger and unwind in reverse order on failure.

## Dependencies and Integration Points

- `spectrum.c` dispatches `ndo_setup_tc` qdisc commands and qevent block binders to this file. Port creation calls `mlxsw_sp_tc_qdisc_init()` after FID setup; port error paths and removal call `mlxsw_sp_tc_qdisc_fini()`.
- `spectrum.h` exposes the qdisc and qevent entry points and embeds `struct mlxsw_sp_qdisc_state *qdisc` in `struct mlxsw_sp_port`.
- `reg.h` supplies congestion and scheduler register packing/constants, including CWTP/CWTPM and QEEC fields.
- Port helpers from the Spectrum core program hardware state: `mlxsw_sp_port_ets_set()`, `mlxsw_sp_port_ets_maxrate_set()`, `mlxsw_sp_port_prio_tc_set()`, headroom helpers, cell/byte conversion helpers, and resource queries.
- `spectrum_span.h` and SPAN helpers provide qevent mirror/trap trigger setup.
- Linux tc offload APIs provide `tc_red_qopt_offload`, `tc_tbf_qopt_offload`, `tc_prio_qopt_offload`, `tc_ets_qopt_offload`, `tc_fifo_qopt_offload`, `flow_block_offload`, and `tc_cls_matchall_offload`.
- `spectrum_acl.c` aligns ACL priority actions with this file's eight-priority model by rejecting priorities at or above `IEEE_8021QAZ_MAX_TCS`.

## Risks and Edge Cases

- Error unwinding in qdisc creation is sensitive because software state, headroom mode, and hardware qdisc programming are updated in stages. Failures after partial hardware programming rely on destroy or replacement paths to leave the port consistent.
- `mlxsw_sp_qdisc_destroy()` attempts root headroom reset even if the qdisc node is already empty; callers depend on that behavior when clearing root state.
- Invisible FIFO ordering is subtle. Incorrect `future_handle` or band tracking can attach a FIFO to the wrong future parent or miss a leaf, especially around rapid qdisc replacement.
- PRIO/ETS replacement returns immediately on a per-band hardware programming error. Bands already programmed before the failure are not locally rolled back in `__mlxsw_sp_qdisc_ets_replace()`, so higher-level destroy/retry behavior is important.
- Stats deltas assume monotonically increasing periodic hardware counters and correct baseline updates. Counter wrap, stale periodic stats, or priority remapping can produce incorrect deltas if clean-stat paths are missed.
- Graft handling intentionally rejects shared or mismatched child qdiscs. This protects hardware correctness but means legal Linux qdisc graphs may fall back to software.
- Qevent block handling supports only a narrow matchall shape and at most one filter. User-visible extack messages are critical for diagnosing unsupported actions, counters, chains, or protocols.
- `mlxsw_sp_tc_qdisc_fini()` only frees the qdisc state and does not recursively destroy any remaining qdisc tree; correct teardown ordering must ensure active offloads are already removed or harmless at that point.

## Test Signals

- Build coverage should compile the mlxsw driver with tc, RED, ETS, netlink, and SPAN dependencies enabled.
- Exercise `tc qdisc replace/del/show` for root and nested RED, TBF, PRIO, ETS, and FIFO cases. Confirm unsupported trees return `-EINVAL` or `-EOPNOTSUPP` and leave no stale hardware state.
- Validate RED with valid and invalid min/max thresholds, ECN and nodrop combinations, qevent early-drop mirror/trap, and qevent mark mirror-only behavior.
- Validate TBF rates near `MLXSW_REG_QEEC_MAS_DIS` and burst sizes below, above, non-power-of-two, and valid power-of-two boundaries.
- Validate PRIO/ETS with 1 through 8 bands, priority remaps, inactive bands, grafted children, and class stats after remapping.
- Confirm stats monotonicity and no double-counting across repeated `tc -s qdisc show`, qdisc replacement with the same handle, handle changes, unoffload fallback, and destroy.
- Check port teardown/recreate after qdisc offloads to catch leaked qdisc state, SPAN sessions, analyzed-port references, and headroom mode regressions.
