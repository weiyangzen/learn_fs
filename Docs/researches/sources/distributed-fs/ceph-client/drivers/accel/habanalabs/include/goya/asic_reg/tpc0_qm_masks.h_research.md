# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_qm_masks.h

## Purpose

`tpc0_qm_masks.h` is the generated bitfield map for the Goya TPC0 queue manager. It defines how to compose and decode fields in TPC0 QM global, producer queue, completion queue, command processor, fence, and debug registers.

## Important APIs, Types, and Constants

The API is macro constants. Global fields cover PQF/CQF/CP/DMA enable, stop, flush, protection, error interrupt/message routing, stop-on-error behavior, error capture data, secure and non-secure ASID/MMBP, idle/stop status, and queue error status. PQ fields cover base low/high, size, PI/CI, credit limit, max in-flight, ARUSER flags, push descriptors (`PUSH0` pointer low, `PUSH1` pointer high, `PUSH2` transfer size, `PUSH3` repeat/control), status counters, busy/empty bits, and read-rate limiter controls. CQ fields mirror config, pointer/size/control, status mirror, credit/free/in-flight counters, busy/empty bits, rate limiter, and IFIFO count. CP fields cover message bases, LDMA offsets, fences, status readiness, current instruction, barrier guard, and debug byte. Buffer debug fields expose PQ/CQ buffer address and read data masks.

## Control Flow

No code is present. Goya queue setup combines these masks with addresses from `tpc0_qm_regs.h` while initializing queues, doorbells, CP messages, fences, protection, and reset stop/flush behavior.

## State and Persistence Behavior

The macros are immutable source. The referenced registers carry persistent queue configuration and live queue/CP state; PI/CI, counters, busy bits, errors, and fences change as workloads run.

## Dependencies and Integration Points

This file pairs with `tpc0_qm_regs.h` and the HabanaLabs QMAN command ABI. It is integrated by Goya queue initialization, MMU ASID setup, command submission, error reporting, reset, and synchronization paths.

## Risks

Field mistakes can break command queueing without a compile error: doorbells can target wrong pointer bits, stop/flush may affect the wrong sub-engine, and ASID/protection masks can compromise isolation. Counter masks must remain aligned with diagnostics.

## Test Signals

Readback after queue setup, working PQ pushes and CQ completions, PI/CI movement, CP fence completion, correct ASID/protection values, expected idle/stop status during reset, and error bits after injected PQ/CQ/CP/DMA faults validate this header.
