# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_qm_regs.h

## Purpose

`tpc0_qm_regs.h` is the generated MMIO address map for the Goya TPC0 queue manager block. It exports `mmTPC0_QM_*` register addresses from `0xE08000` through `0xE0830C`.

## Important APIs, Types, and Constants

The constants cover global configuration/protection/error/status, PQ base/size/PI/CI/config/ARUSER/push/status/rate-limiter registers, CQ config/pointer/transfer/control/status/rate-limiter/IFIFO registers, CP message base pairs, LDMA offsets, fence read-data and counters, CP status/current instruction/barrier/debug registers, and PQ/CQ buffer debug address/data registers.

## Control Flow

There are no functions. Runtime queue flow is implemented in the Goya driver: allocate/program PQ memory, clear PI/CI, configure credit limits, program CP LDMA and message base addresses, enable the queue manager, ring doorbells through PI or push registers, then poll or interrupt on completion and fence state.

## State and Persistence Behavior

The header is static generated source. MMIO register values persist across driver operations until reset or reconfiguration. Queue pointers, status counters, CP readiness, fences, and error captures are live state tied to command execution.

## Dependencies and Integration Points

It is used with `tpc0_qm_masks.h`, common `WREG32`/`RREG32` accessors, Goya QMAN setup code, MMU ASID programming, interrupt/error routing, and device reset logic. TPC1/TPC2 QM maps replicate the same layout at shifted base addresses.

## Risks

Wrong addresses can corrupt queue state or prevent TPC0 work submission. The tightly packed PQ/CQ/CP regions make incorrect offset derivation dangerous because neighboring registers are valid and side-effecting.

## Test Signals

Signals include readback of queue configuration, successful TPC0 command execution, PI/CI and in-flight counter movement, completion queue status updates, fence counter progress, correct reset idle/stop transitions, and valid global error capture on fault injection.
