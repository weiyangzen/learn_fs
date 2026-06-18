# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_qos.c

## Purpose
Implements ENETC traffic-control offloads for TSN/QoS: Qbv taprio gate control, CBS credit shaping, ETF/txtime time-specific departure, and PSFP/Qci stream identification, stream filtering, stream gates, policing, and delayed stats.

## Important APIs, Types, and Functions
Exports `enetc_sched_speed_set`, `enetc_setup_tc_taprio`, `enetc_setup_tc_cbs`, `enetc_setup_tc_txtime`, `enetc_setup_tc_psfp`, `enetc_qos_query_caps`, `enetc_setup_tc_block_cb`, `enetc_set_psfp`, `enetc_psfp_init`, and `enetc_psfp_clean`. Key internal structures are `enetc_streamid`, `enetc_psfp_filter`, `enetc_psfp_gate`, `enetc_psfp_meter`, `enetc_stream_filter`, and global `epsfp`.

## Control Flow
Taprio validates GCL length/time ranges and TSD mutual exclusion, allocates a long-format CBDR data buffer, writes gate list data, enables time gating, sends a port GCL command, and updates max SDU/active offloads. CBS validates priority ordering and slope math, computes bandwidth and hiCredit from port speed/sysclk, and writes per-TC registers. ETF toggles TSD per TX ring when Qbv is inactive. PSFP parses cls_flower gate/police actions and Ethernet/VLAN keys, allocates or reuses stream filter/gate/meter objects, programs stream ID/filter/gate/meter CBDR commands with rollback on failure, stores refcounted global software state, and retrieves hardware counters for delayed stats.

## State and Persistence
Hardware state includes PTGCR, port GCL, PTCMSDUR, CBS registers, TSD registers, stream identification entries, stream filter instances, stream gate control lists, and flow meter instances. Software state includes `active_offloads`, TX ring `tsd_enable` and window-drop counters, global PSFP hlist databases, SFI allocation bitmap, device bitmap, refcounts, and per-filter stats deltas.

## Dependencies and Integration Points
Called from PF netdev `ndo_setup_tc` and ethtool/MM paths. Depends on CBDR command sending, ENETC PTP cycle registers, traffic-control APIs, flow dissector/action APIs, mqprio helpers, port mapping, and PSFP capability fields initialized elsewhere.

## Risks
Risks include global PSFP state shared across devices, spinlock coverage around lists versus hardware commands, refcount/list replacement errors, partial rollback after command failures, Qbv/TSD mutual exclusion, cycle time and base-time arithmetic, limited action/key support, and CBS bandwidth/order constraints that may surprise users.

## Test Signals
Use `tc qdisc taprio`, `cbs`, and `etf` with valid/invalid combinations; verify Qbv and TSD reject each other; bind/unbind clsact flower PSFP rules with gate and police actions; read delayed stats; test resource exhaustion; remove devices while rules exist; and run line-rate traffic to validate shaping, drops, and gate schedules.
