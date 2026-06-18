# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_fsp_pri.h

## Purpose
Defines GH100 FSP PRI register range and queue/message-queue head/tail registers.

## Important APIs, Types, And Functions
Exports `NV_PFSP`, indexed `NV_PFSP_MSGQ_HEAD/TAIL(i)`, and `NV_PFSP_QUEUE_HEAD/TAIL(i)` with eight entries each and 32-bit value/address fields.

## Control Flow
Declarative only. FSP communication code advances or observes producer/consumer queue pointers through these registers.

## State And Persistence
Queue head/tail registers are live firmware communication state and persist until queue reset, firmware reset, or driver teardown.

## Dependencies And Integration Points
Integrated with GSP/FSP command queue transport and PRI register access paths.

## Risks
Head/tail races, wrong queue index, or stale pointer replay can desynchronize the driver and FSP firmware.

## Test Signals
FSP message exchange, boot completion, queue pointer traces, and timeout-free firmware RPCs validate usage.
