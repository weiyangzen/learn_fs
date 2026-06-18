# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_cmdq_regs.h

## Purpose

`tpc1_cmdq_regs.h` is the generated command queue address map for Goya TPC1. It exports the same CMDQ schema as TPC0 at TPC1 addresses `0xE49000` through `0xE4930C`.

## Important APIs, Types, and Constants

The `mmTPC1_CMDQ_*` constants cover global enable/stop/protection/error/status registers, CQ configuration and pointer/transfer/control registers, CQ status mirrors and counters, read-rate limiter controls, IFIFO count, CP message base pairs, CP LDMA offsets, four CP fence read-data/count pairs, CP status, current instruction, barrier config, debug, and CQ buffer debug address/data registers.

## Control Flow

The header has no executable logic. Driver code uses these addresses when configuring or diagnosing the TPC1 command queue, programming CQ and CP state, enabling the queue, handling reset stop/flush, and reading completion or error state.

## State and Persistence Behavior

The source is generated and static. The mapped registers store TPC1 command queue configuration and live execution state; pointer/status/error/fence fields change as commands are processed.

## Dependencies and Integration Points

It pairs with the CMDQ bit definitions generated for the same prototype and with the Goya MMIO helpers. It aligns with TPC0/TPC2/TPC3 CMDQ maps, so multi-TPC code can derive per-core offsets rather than special-case register layouts.

## Risks

Using a TPC0 address for TPC1 or applying the wrong offset can control the wrong core. CP message base, LDMA offset, and fence addresses are high impact because they govern synchronization and message writes.

## Test Signals

Readback of TPC1 CMDQ configuration, TPC1 command completion, CQ counter movement, CP readiness/fence progress, reset idle/stop status, and captured error address/data after fault injection validate this address map.
