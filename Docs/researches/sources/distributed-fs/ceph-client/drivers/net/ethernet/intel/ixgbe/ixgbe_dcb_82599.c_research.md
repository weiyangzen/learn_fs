# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb_82599.c

## Purpose
`ixgbe_dcb_82599.c` programs DCB hardware for the 82599-family MACs, including 82599, X540, X550, X550EM_x, and x550em_a. It configures RX/TX packet and descriptor arbiters, UP-to-TC maps, priority flow control, and queue statistics for the newer register layout.

## Important APIs, Types, And Functions
- `ixgbe_dcb_config_rx_arbiter_82599()` disables RX arbitration, programs `RTRUP2TC`, writes `RTRPT4C` per-TC credits/BWG/link-strict bits, then reenables recycle/WSP arbitration.
- `ixgbe_dcb_config_tx_desc_arbiter_82599()` clears per-queue descriptor credits, writes per-TC `RTTDT2C` credits and strict-priority flags, then enables descriptor-plane arbitration.
- `ixgbe_dcb_config_tx_data_arbiter_82599()` disables TX packet arbitration, programs `RTTUP2TC`, writes `RTTPT2C` credits/BWG/strict-priority flags, then reenables SP/recycle arbitration with DCB arbitration delay.
- `ixgbe_dcb_config_pfc_82599()` switches TX flow control to priority mode, configures RX PFC in `MFLCN`, maps priority PFC bits through `prio_tc`, writes per-TC thresholds and pause timers, and clears unused TC thresholds.
- `ixgbe_dcb_config_tc_stats_82599()` maps RX and TX queues to TC statistic counters according to 82599-family queue allocation.
- `ixgbe_dcb_hw_config_82599()` applies the full backend in fixed order.

## Control Flow
The generic DCB layer supplies arrays of refill credits, max credits, bandwidth group IDs, priority types, and priority-to-TC mappings. RX and TX data arbiters first disable their arbiter before changing UP-to-TC and credit registers, then enable arbitration. TX descriptor arbitration clears 128 per-queue credit contexts because DCB uses per-TC registers instead. PFC configuration derives the highest TC from `prio_tc`, checks whether any priority mapped to each TC has PFC enabled, and chooses PFC thresholds or fallback internal-switch high-water thresholds.

## State And Persistence
The file persists no filesystem state. It mutates MMIO state governing DCB arbitration, UP-to-TC mapping, PFC behavior, pause timers, and queue-statistic attribution. Effects last until reset or another DCB reconfiguration. It reads `hw->fc.low_water`, `high_water`, and `pause_time`.

## Dependencies And Integration Points
It depends on `ixgbe_dcb.h` for generic DCB arrays and on `ixgbe_dcb_82599.h` for register masks/shifts. It is selected by `ixgbe_dcb.c` for 82599-family MAC types and used indirectly by DCBNL CEE/IEEE handlers.

## Risks
- UP-to-TC map and PFC enable masks use different domains: PFC enable is priority-indexed while thresholds are TC-indexed. Errors pause the wrong traffic.
- `MFLCN` handling differs for X540/X550, which support per-TC RX priority flow control; older 82599 behavior uses global RPFCE.
- Fallback high-water programming subtracts 24 KiB from RX packet-buffer size to prevent internal switch TX hangs; removing it can regress virtualization/internal-switch loads.
- Queue statistics mapping is hard-coded to the nonuniform TX queue layout and must match queue allocation.
- Arbiter-disable ordering protects against transient inconsistent hardware programming.

## Test Signals
Validate on 82599 and X540/X550-class devices with IEEE ETS and CEE configurations, UP-to-TC readback, per-priority PFC traffic tests, congestion tests with internal switching/SR-IOV enabled, queue-statistics attribution, 8-TC bandwidth distribution, and repeated reset/reapply of DCB configuration.
