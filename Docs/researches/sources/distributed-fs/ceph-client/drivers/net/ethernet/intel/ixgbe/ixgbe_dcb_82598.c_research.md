# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82598.c

## Purpose
`ixgbe_dcb_82598.c` programs DCB hardware for the 82598 MAC. It configures receive arbitration, transmit descriptor arbitration, transmit data arbitration, priority flow control, and traffic-class statistics mappings using the register layout and limitations of 82598.

## Important APIs, Types, And Functions
- `ixgbe_dcb_config_rx_arbiter_82598()` enables UP-to-queue mapping, receive recycle/DFP arbitration, writes `RT2CR` credit registers, enables multi-packet-buffer and multi-core receive behavior, and clears descriptor bypass.
- `ixgbe_dcb_config_tx_desc_arbiter_82598()` enables descriptor arbitration, TSO expand behavior, max TSO sizing, and per-TC `TDTQ2TCCR` credits and priority flags.
- `ixgbe_dcb_config_tx_data_arbiter_82598()` enables data-plane DFP/recycle arbitration, writes `TDPT2TCCR` credits/priority flags, and enables TX packet-buffer division.
- `ixgbe_dcb_config_pfc_82598()` switches from 802.3x flow control to priority flow control, enables RX PFC when requested, writes per-TC low/high thresholds, pause timers, and refresh threshold.
- `ixgbe_dcb_config_tc_stats_82598()` maps RX/TX queues to TC statistic counters.
- `ixgbe_dcb_hw_config_82598()` is the aggregate backend called from generic DCB dispatch.

## Control Flow
The aggregate configuration function runs in fixed order: RX arbiter, TX descriptor arbiter, TX data arbiter, PFC, then TC statistics. Each arbiter function reads a control register, clears arbitration-disable bits or sets arbitration mode bits, then iterates over `MAX_TRAFFIC_CLASS` to write per-TC refill/max/BWG/strict-priority fields. PFC configuration iterates over all TCs and either disables thresholds or writes `FCRTL/FCRTH` according to `hw->fc.low_water`, `high_water`, and the PFC enable mask.

## State And Persistence
The file writes only adapter hardware registers. Persistent runtime effects include changed DCB arbitration, queue-statistic mapping, packet-buffer division, PFC receive/transmit mode, and pause timing until reset or later reconfiguration. It reads flow-control watermarks from `struct ixgbe_hw`.

## Dependencies And Integration Points
It depends on generic DCB structures from `ixgbe_dcb.h` and 82598-specific register definitions from `ixgbe_dcb_82598.h`. It is called by `ixgbe_dcb.c` for `ixgbe_mac_82598EB`, and by DCBNL-driven reconfiguration through the generic DCB dispatch path.

## Risks
- 82598 has distinct register names and arbitration semantics from 82599; using 82599-style priority maps here would be wrong.
- PFC uses TC-indexed bits directly, while 82599 PFC maps priorities to TCs; this difference matters when changing shared DCB code.
- TSO max credit and descriptor-plane programming are required to avoid stalls with large TX packets.
- Queue-statistic mappings are hard-coded to the 82598 queue layout and can become wrong if queue allocation changes.

## Test Signals
Use 82598 hardware or emulation to verify DCB enablement, RX/TX arbitration registers, PFC pause behavior per TC, TSO traffic under DCB, queue statistics attribution, reset/reapply behavior, and traffic-generator bandwidth distribution across all configured traffic classes.
