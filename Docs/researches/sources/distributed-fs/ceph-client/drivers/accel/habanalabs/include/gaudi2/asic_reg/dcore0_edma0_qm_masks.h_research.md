<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_masks.h

## Purpose
`dcore0_edma0_qm_masks.h` is the generated bitfield map for the DCORE0 EDMA0 queue manager, prototype `QMAN`. It defines 766 shift/mask macros for global queue enable/stop/flush, error reporting, AXI attributes, PQ/CQ/CP programming, completion queues, fences, arbiters, ARC completion queue, address overrides, secure push controls, SEI, local-to-host filtering, rate limiting, indirect APB access, and performance counters.

## Important APIs, types, and functions
The macro surface covers global `PQF`, `CQF`, `CP`, and `ARC_CQF` enable/stop/flush fields; error config/status/message-enable fields including CP undefined command, stop-op, message write, WREG, fence overflow/underflow, CPDMA overflow, CQ CI errors, ARC CQ errors, ARC AXI error, and CP switch watchdog; protection and AXCACHE fields; PQ and CQ base/size/producer/consumer fields; CP message bases, fence controls/counts/data, barrier and LDMA offsets, status/current instruction/predicate/debug/credit/input data fields; PQC HBW/LBW bases, size, PI, config, secure push, and status; arbiter masks, weights, master credits, choice push offsets, slave enables, watchdog/id/quiet/max-inflight/base/state/error fields; ARC CQ config/pointers/status/message bases; CQ CI registers; CP config/switch watchdog; engine/QM/ARC base/range registers; SEI status/mask; global error address/data; L2H compare/mask; local range; rate limit; indirect gateway; and free/idle performance counter fields.

## Control flow
This header has no executable control flow, but it describes the control surface for EDMA0 queue execution. Initialization composes global enable values, programs queue bases/sizes/PIs, configures CP and arbiter policy, enables error reporting, sets AXI/cache/protection attributes, and then permits packet submission. Runtime submission updates producer indexes and relies on CP/CQ/fence machinery. Recovery paths stop/flush PQF/CQF/CP/ARC_CQF, decode error/status fields, drain arbiters, and reset or reinitialize affected queues.

## State and persistence behavior
The QMAN holds extensive persistent hardware state: queue bases and sizes, producer/consumer indices, fence counters, arbiter credits and policy, ARC CQ pointers, CP current instruction/predicate state, secure-push controls, error masks, and performance counter configuration. Status and counters evolve with traffic. Partial reset or incomplete teardown can leave stale queue pointers or credits that corrupt later submissions.

## Dependencies and integration points
This mask header is coupled to `dcore0_edma0_qm_regs.h`, EDMA0 QMAN firmware/driver setup, packet submission, interrupt/error handling, ARC auxiliary control, AXUSER programming, and completion queue handling. It represents one generated `QMAN` prototype instance, so common QMAN code may reuse logic across engines with different macro prefixes.

## Risks and edge cases
Risks include off-by-one queue index handling across 4 PQF, 5 CQF/CP-style lanes, and the ARC CQ path; using read/clear/status masks on wrong register variants; masking serious CP or ARC errors; programming queue base high/low words inconsistently; secure-push misconfiguration; and treating arbiter credit state as stateless after reset. Because many fields repeat by lane, copy/paste mistakes are likely.

## Test signals
Strong validation includes queue bring-up, packet submission/completion, CP fence overflow/underflow injection, CP undefined-command handling, CQ CI error handling, ARC CQ traffic, arbiter fairness/credit behavior, secure and nonsecure push cases, stop/flush recovery, SEI interrupt paths, and free/idle performance counters matching observed activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_masks.h -->
