# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_tsn.c

## Purpose
`igc_tsn.c` implements IGC Time-Sensitive Networking offload programming: frame preemption, MAC merge verification packets, taprio/Qbv gate scheduling, ETF/launchtime support, credit-based shaper/Qav setup, strict queue priority, RX/TX packet buffer sizing, and i226-specific retry-buffer workarounds.

## Important APIs, Types, and Functions
Public entry points are `igc_fpe_init()`, `igc_fpe_clear_preempt_queue()`, `igc_fpe_save_preempt_queue()`, `igc_fpe_get_supported_frag_size()`, `igc_tsn_adjust_txtime_offset()`, `igc_tsn_is_taprio_activated_by_user()`, `igc_tsn_reset()`, and `igc_tsn_offload_apply()`. Internal helpers build and transmit SMD-V/SMD-R frames, map preemptible traffic classes to queues, compute new TSN flags, program TX arbitration, update RX packet buffer sizes, disable TSN registers to defaults, and enable full TSN offload register state.

## Control Flow
FPE initialization installs `ethtool_mmsv_ops`. Ettool MAC merge callbacks update `adapter->fpe.tx_enabled` and can send verification/response SMD frames through a selected TX ring. TSN configuration is applied via `igc_tsn_offload_apply()`: if enabling or disabling TSN would change hardware TX mode while the netdev is running, it schedules an adapter reset; otherwise it calls `igc_tsn_reset()` directly. `igc_tsn_reset()` adds or removes the empty MAC filter needed by preemption, computes TSN flags, disables offload if none are active, or writes the complete TSN register set.

## State and Persistence Behavior
Driver state lives in adapter flags, `taprio_offload_enable`, `strict_priority_enable`, `base_time`, `cycle_time`, `qbv_count`, each TX ring's start/end time, CBS, launchtime, and preemptible flags, plus `adapter->fpe` MAC merge state. Hardware state is in `TQAVCTRL`, `GTXOFFSET`, `TXPBS`, `RXPBS`, `DTXMXPKTSZ`, `TXQCTL`, `STQT`, `ENDQT`, `QBVCYCLET`, `BASET`, `TXARB`, `TQAVCC`, `TQAVHC`, and i226 `RETX_CTL`. Reset paths reconstruct hardware state from driver state.

## Dependencies and Integration Points
The file integrates with ethtool MAC merge verification, tc-mqprio preemptible TC configuration, taprio/launchtime ring settings, IGC TX descriptor formatting, DMA mapping, queue locks, netdev queue accounting, and hardware helpers from `igc.h`, `igc_base.h`, and register definitions.

## Risks and Edge Cases
SMD frame injection uses atomic allocation, DMA mapping, queue locks, descriptor availability, and TX flush ordering. TSN base time is adjusted if already in the past; i226 future scheduling uses `FUTSCDDIS` and an hrtimer path, making timing sensitive. CBS is only configured for queues 0 and 1. FPE queue state depends on `tx_enabled`, `pmac_enabled`, and saved preemptible TCs. Reset scheduling is required when the hardware TX mode changes.

## Test Signals
Exercise taprio enable/disable with base times in the past and future, CBS on queues 0/1 and ignored queues 2/3, launchtime-only mode, strict priority and reversed arbitration, MAC merge verification exchange, preemptible TC mapping from mqprio, i225 versus i226 register behavior, and reset while TSN settings are active.
