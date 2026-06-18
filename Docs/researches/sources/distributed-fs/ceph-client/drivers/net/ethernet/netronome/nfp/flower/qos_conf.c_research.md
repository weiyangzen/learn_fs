<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/qos_conf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/qos_conf.c

## Purpose
`qos_conf.c` implements Flower QoS offload for tc matchall police rate limiters on VF representors and shared tc police actions as firmware meters. It sends QoS add/delete/stats control messages and maintains cached delayed hardware stats for both ingress port policers and action meters.

## Important APIs, Types, And Functions
The main exported functions are `nfp_flower_setup_qos_offload()`, `nfp_flower_qos_init()`, `nfp_flower_qos_cleanup()`, `nfp_flower_stats_rlim_reply()`, `nfp_flower_stats_meter_request_all()`, `nfp_act_stats_reply()`, `nfp_setup_tc_act_offload()`, `nfp_init_meter_table()`, `nfp_flower_setup_meter_entry()`, `nfp_flower_search_meter_entry()`, and `nfp_flower_offload_one_police()`.

## Control Flow
Ingress matchall replace validates firmware VF rate-limit support, representor type, non-shared block, VF port type, priority 1, police action count, action semantics, and BPS/PPS support. It sends one or two QoS_MOD messages and starts the delayed stats poller on the first active limiter. Destroy clears the per-representor QoS table, decrements the shared limiter count, cancels work when count reaches zero, and sends QoS_DEL for BPS and optionally PPS. Stats commands return deltas from the cached current/previous values.

Shared police actions are handled through `nfp_setup_tc_act_offload()`. Replace validates police actions, creates/updates a meter table entry keyed by `hw_index`, sends meter QoS_MOD, and starts the same poller. Destroy sends QoS_DEL with the meter flag and removes the table entry. Stats compute pass/dropped deltas from cached meter stats.

## State And Persistence
State lives in `repr_priv->qos_table` for per-port rate limiters and `priv->meter_table` for action meters. `qos_rate_limiters` counts both kinds of active objects and controls the delayed `qos_stats_work`. Per-port stats use `qos_stats_lock`; meter stats and table walking use `meter_stats_lock`. Firmware state is represented by `NFP_FLOWER_CMSG_TYPE_QOS_MOD`, `QOS_DEL`, and `QOS_STATS`.

## Dependencies And Integration Points
The file integrates with tc matchall, tc action offload, NFP representor ports, Flower feature flags `NFP_FL_FEATS_VF_RLIM`, `NFP_FL_FEATS_QOS_PPS`, and `NFP_FL_FEATS_QOS_METER`, and firmware police message formats. `offload.c` calls this from direct block callbacks and indirect no-netdev action setup.

## Risks
`qos_rate_limiters` is shared between per-port rate limiters and meters, so imbalanced add/delete paths can leave stats work running or canceled prematurely. Some install loops continue after unsupported rate entries and may report success if at least one action was added. Destroy assumes the firmware can safely clear unconfigured BPS/PPS entries. Stats are delayed and delta-based, so counter wrap or firmware reset can produce zeroed deltas due to defensive comparisons in meter stats but not in per-port stats.

## Test Signals
Test VF-only matchall replace/destroy/stats, non-VF rejection, shared block rejection, priority rejection, BPS and PPS combinations with/without firmware PPS support, police conform/exceed action validation, shared action add/delete/stats, meter-table duplicate add, delayed stats polling start/cancel behavior, and firmware stats replies for ingress and meter messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/qos_conf.c -->
