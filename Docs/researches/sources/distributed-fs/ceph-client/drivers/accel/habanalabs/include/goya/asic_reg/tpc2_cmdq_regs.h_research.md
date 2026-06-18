# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_cmdq_regs.h

## Purpose

`tpc2_cmdq_regs.h` is the generated command queue MMIO map for Goya TPC2. It exports `mmTPC2_CMDQ_*` addresses from `0xE89000` through `0xE8930C`.

## Important APIs, Types, and Constants

The address families include global configuration/protection/error/status, CQ configuration/ARUSER/pointer/transfer/control/status/rate-limiter/IFIFO registers, CP message base address pairs, LDMA offsets, fence read-data and counter registers, CP status/current instruction/barrier/debug, and CQ buffer debug address/data registers.

## Control Flow

No functions are defined. Goya queue code uses these constants to program and control the TPC2 command queue, including CQ setup, CP message/fence setup, stop/flush during reset, and error/status reads.

## State and Persistence Behavior

Hardware register values persist until reset or driver updates. CQ pointers/status, CP readiness, current instruction, fences, and error capture registers change while TPC2 commands execute.

## Dependencies and Integration Points

It pairs with CMDQ field masks and aligns with the replicated CMDQ layout for other TPC instances. Integration points are command submission, queue diagnostics, reset, fault handling, and synchronization paths.

## Risks

Using the wrong TPC command queue base can control another core. Misaddressing CP LDMA, message, or fence registers can break command processor progress and completion signaling.

## Test Signals

Readback of configured TPC2 CMDQ registers, command completion, CQ in-flight/free counter changes, CP fence progress, idle/stop status during reset, and expected captured error address/data under fault injection validate the map.
