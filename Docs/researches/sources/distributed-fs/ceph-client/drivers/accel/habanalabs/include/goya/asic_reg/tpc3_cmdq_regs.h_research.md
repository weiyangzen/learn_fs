# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_cmdq_regs.h

## Purpose

`tpc3_cmdq_regs.h` is the generated command queue MMIO map for Goya TPC3. It exports `mmTPC3_CMDQ_*` addresses from `0xEC9000` through `0xEC930C`.

## Important APIs, Types, and Constants

The constants define global command queue configuration/protection/error/status registers, CQ configuration and pointer/transfer/control/status/rate-limiter/IFIFO registers, CP message base pairs, CP LDMA offsets, fence read-data and counters, CP status, current instruction, barrier config, debug register, and CQ buffer debug address/data registers.

## Control Flow

There is no code in this header. Driver paths use the addresses to configure the TPC3 command queue, enable or stop/flush it, program CP message and fence behavior, and read status or captured errors.

## State and Persistence Behavior

The generated file is static source. The mapped registers hold persistent queue configuration and live command processor/completion state for TPC3 until reset or reprogramming.

## Dependencies and Integration Points

It pairs with CMDQ field masks for the shared prototype and common HabanaLabs register accessors. It integrates with TPC3 command submission, reset, synchronization, and fault handling and mirrors the TPC0/TPC1/TPC2 CMDQ layout at the TPC3 base address.

## Risks

Address errors can control the wrong queue or leave TPC3 unable to process commands. CP message, LDMA, fence, and CQ pointer/control registers are high risk because they directly affect completion and synchronization.

## Test Signals

Validation includes readback of programmed TPC3 CMDQ registers, successful TPC3 command execution, CQ counter and pointer status changes, CP fence progress, idle/stop state during reset, and expected error capture on injected command queue faults.
