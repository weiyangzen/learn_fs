<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/main.h

## Purpose
This header defines the ABM app's shared model for queue-management and RED/GRED qdisc offload on NFP NICs. It provides app-level capability/configuration state, per-link qdisc tracking state, statistics formats, action enums, helper predicates, and prototypes used by ABM control, qdisc, classifier, and priority-map code.

## Important APIs, Types, And Functions
- `struct nfp_abm` holds firmware capability data such as `red_support`, `num_prios`, `num_bands`, supported action bitmask, threshold/action arrays, DSCP mask, devlink eswitch mode, and runtime symbols for queue levels and stats.
- `enum nfp_abm_q_action` describes firmware actions for congestion thresholds: mark/drop, mark/queue, drop, queue, and noqueue.
- `struct nfp_alink_stats` and `struct nfp_alink_xstats` model queue counters read from firmware and exposed back to TC qdisc stats.
- `enum nfp_qdisc_type` and `struct nfp_qdisc` represent tracked Linux qdisc objects, including MQ children and RED/GRED per-band parameters, current stats, and previous reported stats.
- `struct nfp_abm_link` ties an ABM app to one data vNIC, its PCIe queue base/count, DSCP/default-band policy, root qdisc, and radix tree of qdiscs.
- Inline helpers `nfp_abm_has_prio()`, `nfp_abm_has_drop()`, and `nfp_abm_has_mark()` centralize capability checks.
- Exported prototypes connect this header to qdisc setup, control-memory access, queue action/level programming, stats reads, queue manager enable/disable, and priority-map updates.

## Control Flow
The header is declarative, but it shapes runtime flow: TC qdisc setup code records qdiscs in `nfp_abm_link.qdiscs`, marks offload candidates, and uses control helpers to program thresholds/actions into firmware. Stats reads populate `struct nfp_alink_stats`/`xstats`, with previous snapshots retained in `struct nfp_qdisc` so later TC stat dumps can report deltas. Per-link priority and DSCP state guide RED versus GRED eligibility and band selection.

## State And Persistence
All state is in kernel memory plus firmware-visible queue configuration. `thresholds`, `threshold_undef`, and `actions` mirror firmware settings; `root_qdisc`, `qdiscs`, qdisc `use_cnt`, `offload_mark`, and `offloaded` represent Linux qdisc hierarchy state. No disk persistence exists. Hardware/firmware state persists only until app reset, queue-manager disable, or explicit reprogramming.

## Dependencies And Integration Points
The header depends on Linux `devlink`, packet classifier/scheduler APIs, radix trees, lists, and NFP app/netdev forward declarations. It is consumed by ABM qdisc code, ABM control code, repr classifier setup, devlink eswitch handling, and NFP app lifecycle code.

## Risks And Edge Cases
- `NFP_QDISC_UNTRACKED` is a sentinel pointer value, so child-pointer users must always test through `nfp_abm_qdisc_child_valid()`.
- `MAX_DPs` bounds GRED bands, while firmware `num_bands` drives loops; capability parsing must ensure these remain compatible.
- Queue indexes combine link `queue_base`, per-link `total_queues`, and global `NFP_NET_MAX_RX_RINGS`; mistakes can program another link's thresholds.
- Stats are snapshot/delta based, so missed initialization or offload-stop transitions can produce negative-looking deltas after unsigned subtraction.
- The structs are shared between TC callbacks, app cleanup, and firmware control paths under RTNL or app-level serialization assumptions not expressed in the header.

## Test Signals
Useful signals include TC RED/GRED/MQ offload success, offload rejection messages for unsupported actions or band counts, correct queue thresholds/actions in firmware, stable qdisc refcounts on graft/destroy/unregister, accurate qdisc stats deltas, DSCP priority-map behavior, and clean app teardown with empty qdisc trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/main.h -->
