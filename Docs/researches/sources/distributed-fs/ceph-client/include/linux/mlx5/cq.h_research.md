# sources/distributed-fs/ceph-client/include/linux/mlx5/cq.h

## Purpose
Defines mlx5 core CQ state, CQE syndrome/opcode enums, modification parameters, stride encodings, doorbell helpers, refcount helpers, and CQ management APIs.

## Important APIs/Types
`struct mlx5_core_cq` holds CQN, CQE size, doorbell records, refcount/free completion, vector/IRQ, callbacks, consumer index, arm sequence, debug handle, PID, tasklet context, reset notifier, EQ pointer, and UID. Enums define syndromes, CQE opcodes, modify masks, resize opmods, stride values, and DB request commands. Helpers set CI, arm CQs, hold/put refs, dump error CQEs, and map CQE size to firmware stride. APIs create/destroy/query/modify CQs, modify moderation, add tasklet work, and manage debug tracking.

## Control Flow
Users create CQs, process CQEs, update CI, arm interrupts by writing host memory then MMIO, and hold references while callbacks/events run. Final put completes teardown.

## State And Persistence
CQ state includes firmware CQN, doorbell records, consumer index, arm sequence, callbacks, EQ binding, debug object, reset notifier, and UID. Rings and doorbells are hardware-shared.

## Dependencies And Integration Points
Depends on mlx5 driver/EQE types, refcounting, completions, and doorbell writes. Integrates with mlx5_core, mlx5e, mlx5_ib, EQ tasklets, debug/resource tracking, and reset notification.

## Risks
Wrong stride selection, missing barrier before MMIO, refcount leaks/use-after-free, moderation field overflow, and 32-bit doorbell atomicity assumptions.

## Test Signals
CQ create/query/modify/destroy, moderation, resize, CI updates, interrupt arming, tasklet callbacks, error CQE dumps, reset notifiers, and final-ref completion.
