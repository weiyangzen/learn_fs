# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_nrtr_masks.h

## Purpose

`tpc0_nrtr_masks.h` defines bitfields for the Goya TPC0 north-router/interface router block. The fields configure HBW/LBW credits, debug arbitration, split/rate behavior, address range matching, regulator control, and scrambling.

## Important APIs, Types, and Constants

The exported macros are `_SHIFT` and `_MASK` constants. HBW/LBW max credit fields split write request, write response, read request, and read response credits into 6-bit lanes. Debug arbitration fields encode route weights for east, west, north, south, and local directions, with separate max-credit fields. Split controls include ten split coefficient registers, default mesh selection, forced weak/strong ordering, read/write rate limiter enables, back-to-back optimization, saturation, reset token, and timeout fields. Range fields cover HBW hit bitmap, 8 HBW mask/base low/high pairs, LBW hit bitmap, and 16 LBW mask/base pairs. Regulator fields expose read/write enable and result values. Scrambler fields enable linear and non-linear scrambling.

## Control Flow

There is no code. Initialization or performance-tuning paths write credit/arbitration/range/split fields, while diagnostics read result and range hit fields to understand routing decisions.

## State and Persistence Behavior

Macros are static constants. Router configuration persists in hardware until reset or reprogramming; hit/result fields reflect live or latched routing behavior.

## Dependencies and Integration Points

This header pairs with `tpc0_nrtr_regs.h`. It relates to mesh routing, memory fabric access, HBW/LBW address decoding, QoS/credit tuning, and low-level register programming for TPC0 traffic.

## Risks

Misprogrammed credits or arbitration can deadlock or starve traffic. Incorrect range masks/bases can route memory transactions to the wrong fabric path. Scrambler and ordering bits affect correctness and performance and should be changed only with silicon guidance.

## Test Signals

Test signals include expected HBW/LBW range hit bits for known addresses, no starvation under mixed read/write load, rate limiter saturation/token behavior, regulator result values after read/write enable, and stable traffic behavior with scrambling enabled or disabled.
