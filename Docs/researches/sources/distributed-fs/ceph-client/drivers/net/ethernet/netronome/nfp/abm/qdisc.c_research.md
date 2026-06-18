<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/qdisc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/qdisc.c

## Purpose
This file implements TC qdisc tracking and offload programming for the NFP ABM app. It supports root/MQ/RED/GRED setup callbacks, maintains a local qdisc hierarchy, compiles eligible RED/GRED leaves into firmware queue levels/actions, reads firmware queue stats, and translates hardware counters back into Linux qdisc statistics.

## Important APIs, Types, And Functions
- Entry points: `nfp_abm_qdisc_offload_update()`, `nfp_abm_setup_root()`, `nfp_abm_setup_tc_red()`, `nfp_abm_setup_tc_mq()`, and `nfp_abm_setup_tc_gred()`.
- Qdisc tree helpers: `nfp_abm_qdisc_alloc()`, `nfp_abm_qdisc_free()`, `nfp_abm_qdisc_find()`, `nfp_abm_qdisc_replace()`, `nfp_abm_qdisc_destroy()`, `nfp_abm_qdisc_graft()`, and `nfp_abm_qdisc_unlink_children()`.
- Offload compiler: `nfp_abm_offload_compile_mq()` walks MQ children and `nfp_abm_offload_compile_red()` validates RED/GRED leaves and programs `nfp_abm_ctrl_set_q_lvl()` and `nfp_abm_ctrl_set_q_act()`.
- Parameter checks: `nfp_abm_red_check_params()` and `nfp_abm_gred_check_params()` enforce firmware-supported ECN/drop action, harddrop absence, min/max equality, threshold bounds, default band, and band count.
- Stats path: `nfp_abm_stats_update()`, `nfp_abm_stats_update_mq()`, `nfp_abm_stats_update_red()`, `nfp_abm_stats_init()`, `nfp_abm_stats_calculate()`, and `nfp_abm_stats_red_calculate()`.

## Control Flow
TC setup first creates or finds qdisc records by major handle in `alink->qdiscs`. Root setup adjusts the root use count and calls `nfp_abm_qdisc_offload_update()`. MQ creation creates a child table sized to `alink->total_queues`; MQ graft links per-queue children and increments child `use_cnt`. RED/GRED replace records parameters and updates offload only when attached.

`nfp_abm_qdisc_offload_update()` clears firmware threshold-defined bits for this link, clears all qdisc `offload_mark`s, recompiles the current root MQ tree, flips `offloaded` state, stops stale offloads, resets unconfigured thresholds to `NFP_ABM_LVL_INFINITY`, and forces a stats refresh. A plain RED qdisc is offloadable only as a single attached leaf without priority bands or children. GRED is offloadable when parameters are valid and the qdisc has one attachment. MQ is the root fanout that maps child RED/GRED qdiscs to hardware queues.

Stats are rate-limited by `NFP_ABM_STATS_REFRESH_IVAL`. Firmware counters are read only for offloaded RED/GRED children. TC stats commands compute deltas from previous snapshots and update the previous snapshots after reporting. MQ stats are synthesized by summing child RED/GRED band counters because Linux core aggregates MQ child stats differently.

## State And Persistence
Persistent storage is not used. Runtime state lives in the `nfp_abm_link` qdisc radix tree and `struct nfp_qdisc` instances: hierarchy child pointers, use counts, parameter validity, offload status, thresholds/actions, and stats snapshots. Firmware-visible state includes queue levels, queue actions, and stats counters accessed through ABM control helpers. On offload stop, backlog counters are reset after they can be reported back through TC.

## Dependencies And Integration Points
The file integrates Linux RTNL/TC qdisc offload APIs (`tc_red_qopt_offload`, `tc_gred_qopt_offload`, `tc_mq_qopt_offload`, root qdisc offload), generic qdisc stats helpers, Netronome app/netdev/port structures, firmware control helpers declared in `abm/main.h`, and `nfp_port.tc_offload_cnt` accounting.

## Risks And Edge Cases
- MQ destruction during netdev unregister is special-cased because MQ does not always notify child destruction cleanly.
- Child `use_cnt` correctness depends on every graft, root change, destroy, and unregister path being balanced.
- The qdisc radix tree key uses `TC_H_MAJ(handle)`, so duplicate major handles are impossible and handle misuse can collide.
- Parameter rejection leaves qdisc records present but `params_ok == false`; later graft/root updates must keep rejecting offload while retaining software TC behavior.
- Firmware programming calls in `nfp_abm_offload_compile_red()` do not abort on individual set failures, so test logs are important to catch partial programming.
- Stats are rate-limited and delta-based; rapid TC stat polling or offload transitions can hide short-lived firmware counter changes.

## Test Signals
Exercise RED and GRED offload with ECN and drop modes, unsupported harddrop/min-max/WRED/GRIO cases, MQ grafting across multiple queues, root qdisc replacement, netdev unregister cleanup, repeated stats dumps, offload stop/restart preserving backlog deltas, firmware threshold reset to infinity for unconfigured queues, and `tc_offload_cnt` returning to zero after teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/qdisc.c -->
