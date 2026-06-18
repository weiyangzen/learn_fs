# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc1_qm_regs.h

## Purpose

`tpc1_qm_regs.h` is the generated MMIO address map for the Goya TPC1 queue manager, covering `0xE48000` through `0xE4830C`. It is the TPC1 instance of the QMAN prototype.

## Important APIs, Types, and Constants

The `mmTPC1_QM_*` constants include global config/protection/error/status registers, PQ base/size/PI/CI/config/ARUSER/push/status/rate limit registers, CQ config/pointer/transfer/control/status/rate limit/IFIFO registers, CP message base pairs, LDMA offsets, fence read-data and counters, CP status/current instruction/barrier/debug, and PQ/CQ buffer debug access registers.

## Control Flow

This header contains no functions. Goya initialization and command submission code writes these addresses to configure TPC1 queues, program CP message and LDMA behavior, enable/stop/flush the QMAN, submit work, and read completion or fault state.

## State and Persistence Behavior

Register values hold persistent queue configuration and live queue state for TPC1. PI/CI, credit counters, CP status, fences, and error captures mutate during workload execution and reset.

## Dependencies and Integration Points

It integrates with QMAN masks, Goya queue setup, MMU ASID programming, doorbell mapping, interrupt/fault handling, and reset logic. It shares layout with TPC0 and TPC2 queue manager maps at different base addresses.

## Risks

Wrong register addresses can submit commands to the wrong TPC, corrupt TPC1 queue pointers, or misconfigure CP message/fence handling. Because all addresses are valid MMIO, many mistakes surface as hardware hangs rather than immediate software failures.

## Test Signals

Signals include successful TPC1 queue initialization, PI/CI and credit counter movement, CQ completion updates, CP fence increments, expected global idle/stop states during reset, and correct ASID/protection readbacks.
