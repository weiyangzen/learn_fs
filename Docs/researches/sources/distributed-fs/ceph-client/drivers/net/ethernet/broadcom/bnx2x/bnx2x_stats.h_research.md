# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_stats.h

## Purpose
Declares the `bnx2x` statistics state machine events/states, persistent Ethernet statistics structures, old-counter snapshots, NIG stats layout, arithmetic/update macros, and exported statistics APIs. It is the contract used by the stats implementation, core driver paths, ethtool, and SR-IOV teardown synchronization.

## Important APIs, Types, and Functions
Important types are `struct nig_stats`, `enum bnx2x_stats_event`, `enum bnx2x_stats_state`, `struct bnx2x_eth_stats`, `struct bnx2x_eth_q_stats`, `struct bnx2x_eth_stats_old`, `struct bnx2x_eth_q_stats_old`, `struct bnx2x_net_stats_old`, and `struct bnx2x_fw_port_stats_old`. Exported functions are `bnx2x_memset_stats`, `bnx2x_stats_init`, `bnx2x_stats_handle`, `bnx2x_stats_safe_exec`, `bnx2x_save_statistics`, and `bnx2x_afex_collect_stats`.

The macro layer performs 64-bit split-counter arithmetic and counter folding: `ADD_64`, `ADD_64_LE`, `ADD_64_LE16`, `DIFF_64`, `UPDATE_STAT64`, `UPDATE_STAT64_NIG`, `ADD_EXTEND_64`, `ADD_STAT64`, `UPDATE_EXTEND_STAT`, `UPDATE_EXTEND_TSTAT`, `UPDATE_EXTEND_E_TSTAT`, `UPDATE_EXTEND_USTAT`, `UPDATE_EXTEND_E_USTAT`, `UPDATE_EXTEND_XSTAT`, `UPDATE_QSTAT`, `UPDATE_QSTAT_OLD`, `UPDATE_ESTAT_QSTAT_64`, `UPDATE_ESTAT_QSTAT`, `UPDATE_FSTAT_QSTAT`, `UPDATE_FW_STAT`, `UPDATE_FW_STAT_OLD`, `UPDATE_ESTAT`, `SUB_64`, `SUB_EXTEND_64`, and `SUB_EXTEND_USTAT`.

## Control Flow and State
This header has no standalone runtime control flow, but it defines the events and states consumed by `bnx2x_stats_handle`. The structures distinguish total Ethernet counters, per-queue counters, and "old" snapshots used to compute deltas or preserve values over reset/unload. Many fields are split high/low 32-bit values because hardware and firmware counters are exposed as 32-bit words or little-endian split values.

## State and Persistence Behavior
`struct bnx2x_eth_stats` is the long-lived aggregate exported to netdev and ethtool-style consumers. `struct bnx2x_eth_q_stats` tracks per-fastpath queue totals. The `_old` structures intentionally persist selected values across firmware reset or unload, and the macros update those snapshots as deltas are consumed. `struct bnx2x_fw_port_stats_old` preserves MF firmware port discard counters for PMF-owned port stats.

## Dependencies and Integration Points
Includes Linux integer types and forward-declares `struct bnx2x`. It is included by `bnx2x_stats.c` and other driver modules that emit stats events, save statistics, or use safe stats execution. The field names and macro assumptions are tightly coupled to firmware statistics structures in the broader `bnx2x` HSI headers and to the slowpath layout used by DMAE.

## Risks and Test Signals
Risks are mostly structural and arithmetic: field-order changes can break `struct_group` copies, macro call sites depend on local variable names such as `new`, `old`, `pstats`, `estats`, `qstats`, and `diff`, and split-counter arithmetic must handle wrap without negative totals. Test signals include compile coverage for all macro call sites, sparse/endian checks for little-endian macros, stats continuity across reset/unload, 32-bit and 64-bit architecture builds, and ethtool/netdev stat comparisons under traffic, drops, TPA, pause/PFC, and FCoE.
