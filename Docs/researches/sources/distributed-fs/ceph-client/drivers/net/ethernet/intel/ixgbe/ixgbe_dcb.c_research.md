# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_dcb.c

## Purpose
`ixgbe_dcb.c` is the generic Data Center Bridging calculation and dispatch layer. It converts ixgbe DCB configuration structures and IEEE ETS inputs into traffic-class credit arrays, PFC masks, bandwidth group IDs, priority types, and priority-to-traffic-class maps, then delegates hardware programming to 82598 or 82599-family implementations.

## Important APIs, Types, And Functions
- `ixgbe_dcb_calculate_tc_credits()` computes CEE-style per-traffic-class refill and max credits from bandwidth group percentages, traffic-class bandwidth, max frame size, and MAC type.
- `ixgbe_ieee_credits()` computes simplified IEEE 802.1Qaz ETS credits directly from per-TC bandwidth percentages.
- Unpack helpers extract fields from `struct ixgbe_dcb_config`: PFC bitmask, refill credits, max credits, bandwidth group IDs, priority types, and UP-to-TC maps.
- `ixgbe_dcb_get_tc_from_up()` and `ixgbe_dcb_unpack_map()` translate user priorities into traffic classes using configured bitmaps.
- `ixgbe_dcb_hw_config()`, `ixgbe_dcb_hw_pfc_config()`, `ixgbe_dcb_hw_ets()`, and `ixgbe_dcb_hw_ets_config()` select the correct 82598 or 82599-family hardware backend.
- `ixgbe_dcb_read_rtrup2tc()` reads hardware UP-to-TC mapping for 82599-family devices.

## Control Flow
CEE configuration starts from `ixgbe_dcb_hw_config()`: unpack the abstract `ixgbe_dcb_config`, then branch on `hw->mac.type`. The 82598 branch calls the 82598 backend without a priority map; the 82599/X540/X550 branches pass `prio_tc` for UP-to-TC register programming. IEEE ETS configuration flows through `ixgbe_dcb_hw_ets()`, which validates TSA values, maps strict and ETS TSAs onto ixgbe priority types, computes refill/max credits, and calls `ixgbe_dcb_hw_ets_config()`.

Credit calculation first determines minimum credit needed for half the max frame in 64-byte quanta, finds the smallest nonzero bandwidth share, derives a multiplier that keeps refill credits above the minimum frame requirement, then writes refill/max credits back into each TC path. For TX on 82598, descriptor max credits are raised to the TSO minimum if needed.

## State And Persistence
This file does not persist state outside memory and hardware. It mutates `struct ixgbe_dcb_config` by filling `link_percent`, `data_credits_refill`, `data_credits_max`, and `desc_credits_max`. Hardware state changes happen indirectly through backend calls that program DCB arbiter and PFC registers. Input configuration is owned by adapter-level DCB netlink setup.

## Dependencies And Integration Points
The file depends on `ixgbe.h`, `ixgbe_type.h`, `ixgbe_dcb.h`, and chip-specific DCB headers. Its callers include `ixgbe_dcb_nl.c`, adapter traffic-class setup paths, and any reset/reconfigure flow that reapplies DCB. It bridges the Linux DCBNL/IEEE concepts into hardware-specific CEE-like credit programming.

## Risks
- `min_percent` must not remain at an invalid value for all-zero bandwidth inputs; callers are expected to validate DCB rules before credit calculation.
- Integer division can collapse small bandwidth shares to zero, so the code has explicit minimum correction. Changes here can skew actual wire bandwidth.
- 82598 TSO credit handling is special; missing that adjustment can cause TX stalls with large TSO frames.
- Hardware dispatch excludes E610 and unsupported MAC types in this source; callers must account for no-op or `-EINVAL` returns.
- Priority map consistency matters for PFC: mismatched ETS and PFC maps can pause the wrong traffic class.

## Test Signals
Tests should cover CEE and IEEE ETS configurations with 1, 4, and 8 TCs; strict and ETS TSA combinations; very small nonzero bandwidth percentages; jumbo MTU and FCoE-sized frames; 82598 TSO traffic under DCB; PFC enable/disable per priority; hardware readback of UP-to-TC maps; and traffic-generator validation that bandwidth ratios and pause behavior match configuration.
