# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_cmdq_masks.h

## Purpose

`tpc0_cmdq_masks.h` is the generated bitfield companion for the Goya TPC0 command queue register block. It gives callers the `_SHIFT` and `_MASK` values needed to compose or decode fields in the addresses exported by `tpc0_cmdq_regs.h`.

## Important APIs, Types, and Constants

The exported API is preprocessor constants only. Global command queue fields cover enable, stop, flush, protection, error interrupt/message routing, stop-on-error policy, secure and non-secure ASID/MMBP properties, idle/stop status, and read/write/message error status. CQ fields cover credit limits, max in-flight counts, ARUSER nosnoop/word flags, command pointer/transfer/control fields, status mirrors, FIFO counts, read rate limiter tokens/saturation/timeout, and buffer debug access. CP fields cover four message base address pairs, LDMA source/destination/size/commit offsets, fence read-data increments, fence counters, CP readiness/status, current instruction, barrier guard, and debug byte fields.

## Control Flow

There is no executable control flow. Driver code combines these masks with `WREG32`/`RREG32` register accesses when enabling the command queue, stopping or flushing engines, routing faults, setting message bases, and polling CQ/CP state.

## State and Persistence Behavior

The macros do not hold state. The referenced hardware fields persist in MMIO registers until reset or reprogramming; status and error fields are live hardware observations.

## Dependencies and Integration Points

This header pairs directly with `tpc0_cmdq_regs.h` and follows the generated CMDQ schema also used by other TPC command queues. It integrates with the HabanaLabs Goya queue setup, fault handling, MMU/ASID programming, CP message handling, and fence synchronization paths.

## Risks

Incorrect masks can silently enable the wrong sub-engine, clear or assert the wrong stop/flush bit, misroute errors, or corrupt address fields. The CP status and fence fields are especially sensitive because readiness and synchronization decisions depend on exact bit positions.

## Test Signals

Useful signals are readback of configured enable/protection/error bits, CQ credit and in-flight counters changing under command traffic, rate limiting behavior when enabled, correct CP fence counter increments, and expected idle/stop/error bits during reset and fault injection.
