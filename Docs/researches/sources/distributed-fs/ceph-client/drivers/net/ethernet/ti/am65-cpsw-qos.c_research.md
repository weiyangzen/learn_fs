# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-qos.c

## Purpose
Implements traffic-control and time-sensitive networking offloads for AM65 CPSW: MQPRIO queue/priority mapping and shapers, TAPRIO/EST schedule programming, IET/MAC Merge preemption configuration, host TX queue maxrate programming, and simple flower policer offload for broadcast/multicast ALE rate limits.

## Important APIs, Types, and Functions
The public entry points are `am65_cpsw_qos_ndo_setup_tc`, `am65_cpsw_qos_link_up`, `am65_cpsw_qos_link_down`, `am65_cpsw_qos_ndo_tx_p0_set_maxrate`, `am65_cpsw_qos_tx_p0_rate_init`, `am65_cpsw_iet_commit_preemptible_tcs`, and `am65_cpsw_iet_common_enable`. Internal flows center on `am65_cpsw_setup_mqprio`, `am65_cpsw_taprio_replace`, `am65_cpsw_taprio_destroy`, `am65_cpsw_est_set_sched_list`, `am65_cpsw_timer_set`, `am65_cpsw_qos_setup_tc_block`, and clsflower policer helpers.

## Control Flow
`ndo_setup_tc` dispatches query caps, TAPRIO, MQPRIO, and TC block requests. MQPRIO copies qdisc offload state, resumes PM, validates shaper rates, configures Linux traffic classes, writes queue-to-priority mapping into the port TX priority map, applies per-priority CIR/EIR shapers if link bandwidth allows, and updates IET preemptible traffic classes. TAPRIO requires a running link, rejects round-robin P0 RX priority mode and unsupported cycle extensions, applies MQPRIO, allocates a variable-sized EST schedule object, validates fetch RAM command count, selects a free double buffer, writes fetch commands into port fetch RAM, adjusts past base times into the future, enables EST at port/common level, and programs a CPTS ESTF periodic output when needed.

IET flow stores requested preemptible TCs, serializes with `mm_lock`, enables common IET if any port has IET RX enabled, programs verification timeout based on PHY mode and link speed, optionally runs MAC Merge verify polling, and commits the preemption mask only after link and verification. Flower offload only accepts chain-0 policer actions using packet-per-second rate with drop-on-exceed and destination MAC matches for broadcast or multicast, translating those into `cpsw_ale_rx_ratelimit_bc/mc`.

## State and Persistence
QoS state persists in `port->qos`: admin/oper EST schedules, link speed/down time, MQPRIO copy and shaper state, IET preemptible TCs/original max blocks/verify timeout, and ALE rate-limit cookies. Hardware state persists in CPSW global EST/IET enable bits, per-port EST/IET control/status/verify registers, per-priority CIR/EIR shaper registers, priority maps, fetch RAM buffers, CPTS ESTF outputs, and ALE rate-limit entries.

## Dependencies and Integration Points
Depends on `am65-cpsw-nuss.h`, `am65-cpsw-qos.h`, `am65-cpts.h`, `cpsw_ale.h`, runtime PM, TC qdisc/offload APIs, flow block/flower APIs, netlink extack, and phylink link-speed callbacks from the main driver. TAPRIO timing is tied to CPTS through `am65_cpts_ns_gettime`, `am65_cpts_estf_enable`, and `am65_cpts_estf_disable`.

## Risks and Test Signals
Risks include incorrect unit conversion between bytes/sec, Mbps, bus-frequency shaper units, nanoseconds, link-speed fetch counts, and CPTS cycles; touching EST RAM while a buffer transition is in flight; losing TAS after long link-down intervals; sequential high-to-low rate-mask validation surprising users; IET verification timeout miscomputed for PHY modes; and stale policer cookies. Test signals include `tc mqprio` with min/max rates, `tc taprio` base-time/cycle edge cases, `tc filter flower ... police` for broadcast/multicast, link down/up while EST/IET is enabled, PTP/CPTS clock adjustment while schedules run, and register dumps of shaper, EST, IET, and ALE policer state.
