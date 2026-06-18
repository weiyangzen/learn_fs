# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-qos.h

## Purpose
Declares AM65 CPSW QoS state structures, register offsets, bit fields, and optional build stubs. It is the shared contract for TSN/TC support used by the NUSS driver and QoS implementation.

## Important APIs, Types, and Functions
State structs include `am65_cpsw_est`, `am65_cpsw_mqprio`, `am65_cpsw_iet`, `am65_cpsw_ale_ratelimit`, and `am65_cpsw_qos`. Public APIs are conditionally declared or stubbed: `am65_cpsw_qos_ndo_setup_tc`, `am65_cpsw_qos_link_up`, `am65_cpsw_qos_link_down`, `am65_cpsw_qos_ndo_tx_p0_set_maxrate`, `am65_cpsw_qos_tx_p0_rate_init`, `am65_cpsw_iet_commit_preemptible_tcs`, and `am65_cpsw_iet_common_enable`. The file also defines CPSW global/port QoS registers, EST fetch RAM fields, IET MAC Merge fields, FIFO status bits, and IET statistics offsets.

## Control Flow
Runtime control is selected at compile time with `CONFIG_TI_AM65_CPSW_QOS`. When enabled, callers bind to the real implementation. When disabled, TC setup returns `-EOPNOTSUPP`, link callbacks and IET enable/commit are no-ops, and maxrate returns success without hardware programming.

## State and Persistence
The declared QoS structures are embedded per port and keep admin/oper schedules, link information, mqprio shaper copies, IET requested state, and ALE policer cookies across netdev and phylink callbacks. The register macros describe persistent hardware state in CPSW global control, port control, priority maps, shaper registers, EST fetch RAM, MAC Merge control/status/verify, FIFO status, and IET statistics.

## Dependencies and Integration Points
Includes `linux/netdevice.h` and `net/pkt_sched.h`, forward-declares `am65_cpsw_common` and `am65_cpsw_port`, and is included by `am65-cpsw-nuss.h` and `am65-cpsw-qos.c`. It integrates TC qdisc APIs with the main driver's netdev ops and phylink link-state notifications.

## Risks and Test Signals
Risks are mostly hardware ABI and config-stub drift: duplicated register definitions must remain consistent, masks must match hardware, and disabled-QoS stubs must preserve caller expectations. Test signals are enabled/disabled QoS builds, compile coverage of TAPRIO/MQPRIO/flower paths, and hardware tests proving EST/IET/shaper bits land in expected registers.
