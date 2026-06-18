# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mme_qm_masks.h

## Purpose

`mme_qm_masks.h` defines generated bit masks and shifts for the Goya MME queue manager (`MME_QM`) block. It describes both the producer queue (PQ) and completion/command queue (CQ) sides of the QMAN prototype, along with global protection/error state, command processor metadata, fences, and debug buffers.

## Important APIs, types, and data

The file exports `MME_QM_*_SHIFT` and `MME_QM_*_MASK` macros. Global fields cover PQF/CQF/CP/DMA enable, stop, flush, protection, error interrupt/message/stop-on-error policy, captured error address/write data, secure and non-secure ASID/MMBP properties, idle/stop status, and read/undefined-command/message/DMA error status.

PQ-specific fields include base low/high, queue size, producer/consumer indices, credit limit, max inflight, ARUSER no-snoop/word flags, four push words for pointer/size/control, credit/free/inflight/busy/empty status, and read-rate limiter controls. CQ fields mirror pointer, size, control, status, credit, busy, and rate-limit controls. CP fields include four message-base address pairs, LDMA offset registers, four fence read-data/count fields, CP ready/stop/fence status, current instruction, barrier guard, debug byte, and PQ/CQ buffer address/read-data debug access.

## Control flow

The header contains no executable logic. Consumers use it to construct queue-manager register values during queue creation and reset. A normal setup initializes PQ storage and indices, programs CQ and CP metadata, configures secure/non-secure properties and error handling, then enables PQF/CQF/CP/DMA. Submission updates PQ producer state or push registers; completion and diagnostics read CQ/PQ status, CP status, fence counters, and debug buffer windows.

## State and persistence behavior

The macros are compile-time constants. The hardware fields define persistent queue state across submissions: ring base/size/indices, inflight accounting, rate-limiter settings, CP message routing, LDMA offsets, fence counters, and security context. Error capture/status fields are latched device state and must be cleared by the appropriate reset or acknowledgement logic.

## Dependencies and integration points

This file pairs with `mme_qm_regs.h` and common QMAN programming code. It shares many field layouts with `mme_cmdq_masks.h`, but adds PQ-specific fields. It integrates with Goya queue allocation, doorbell handling, MMU ASID propagation, command submission, CP fence handling, and reset logic.

## Risks and edge cases

Queue state is sensitive to ordering. Enabling queue engines before base/size/ASID/CP metadata is valid can produce DMA or translation faults. Producer and consumer indices are full-width fields but ring size is configured separately; callers must keep them modulo the hardware queue length. Busy/empty bits live at high bits in status registers and should not be confused with inflight counters. ASID/MMBP fields are only 10/1 bits, so stale or truncated security context can misroute MME transactions.

## Test signals

Build-time checks should ensure all MME queue paths reference the correct QMAN field names. Runtime signals include queue initialization without stuck busy bits, successful MME command submission through PQ/CQ, correct fence increments, expected stop/flush idle transitions during reset, and accurate error capture when invalid queue descriptors or protected memory accesses are injected.
