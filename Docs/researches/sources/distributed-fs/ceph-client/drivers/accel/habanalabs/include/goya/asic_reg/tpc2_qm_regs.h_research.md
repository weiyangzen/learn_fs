# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc2_qm_regs.h

## Purpose

`tpc2_qm_regs.h` is the generated address map for the Goya TPC2 queue manager block, spanning `0xE88000` through `0xE8830C`.

## Important APIs, Types, and Constants

`mmTPC2_QM_*` constants cover global QMAN control/protection/error/status, producer queue base/size/PI/CI/config/ARUSER/push/status/rate limit registers, completion queue config/pointer/transfer/control/status/rate limit/IFIFO registers, command processor message base pairs and LDMA offsets, four fence read-data/count pairs, CP status/current instruction/barrier/debug, and PQ/CQ buffer debug address/data registers.

## Control Flow

There is no executable code. The driver uses this map to initialize TPC2 queue memory, configure CP message and LDMA behavior, enable the queue manager, submit work through PI/push registers, and inspect completion/error state.

## State and Persistence Behavior

The MMIO registers hold persistent queue configuration and live execution state. Queue pointers, counters, CP state, fences, and global error status mutate as commands are submitted, completed, or reset.

## Dependencies and Integration Points

It is consumed with QMAN masks and common HabanaLabs MMIO routines. It integrates with TPC2 command submission, MMU ASID properties, doorbell lookup, synchronization, interrupt/fault reporting, and reset handling.

## Risks

Address mistakes can corrupt TPC2 queue metadata, send doorbells to the wrong register, or hide queue faults. CP message and fence registers are critical for completion signaling.

## Test Signals

Validation includes TPC2 queue initialization readback, successful command execution, PI/CI movement, PQ/CQ counter changes, CP fence increments, correct global idle/stop status, and expected error captures on injected queue faults.
