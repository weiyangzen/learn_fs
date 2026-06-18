# sources/distributed-fs/ceph-client/drivers/mmc/host/mmc_hsq.h

## Purpose

`mmc_hsq.h` is the private/public header for MMC host software queue support. It defines queue dimensions, queue state structures, and exported helper prototypes used by host drivers that want CQE-style software queueing without a hardware CQE engine.

## Important APIs, Types, And Functions

- `HSQ_NUM_SLOTS` is 64, matching the supported tag array size.
- `HSQ_INVALID_TAG` is the sentinel value equal to `HSQ_NUM_SLOTS`.
- `HSQ_NORMAL_DEPTH` is 2, chosen to limit latency.
- `HSQ_PERFORMANCE_DEPTH` is 5, used by the implementation's 4 KiB random-write heuristic.
- `struct hsq_slot` stores one `struct mmc_request *` per tag.
- `struct mmc_hsq` stores the associated MMC host, active request, wait queue, slot array, lock, retry work, head/tail/tag link state, queue count, and booleans for enabled, waiting-for-idle, and recovery halt.
- Prototypes: `mmc_hsq_init`, `mmc_hsq_suspend`, `mmc_hsq_resume`, and `mmc_hsq_finalize_request`.

## Control Flow And State

The header defines the persistent state that `mmc_hsq.c` mutates. `slot[]` maps tags to requests; `tag_slot[]` acts as a linked list of queued tags; `next_tag` and `tail_tag` define the queue; `mrq` is the single currently submitted hardware request; and the boolean flags coordinate enable/disable and recovery behavior.

## Dependencies And Integration Points

This header relies on MMC core types being visible to users. It is included by `mmc_hsq.c` and host drivers embedding `struct mmc_hsq`. The finalization API is the key integration point for underlying host-completion paths.

## Risks And Edge Cases

- Queue size is fixed at 64; host tags must be within that range.
- `HSQ_INVALID_TAG` is a valid array length but invalid index; callers must never index with it.
- The header exposes internal structure layout, so host drivers can embed but should not mutate fields directly outside the helper API.

## Test Signals

Signals are mostly compile-time and integration-level: embedded `struct mmc_hsq` size/layout, successful `mmc_hsq_init()`, valid CQE callback registration, and finalization from a host driver with request tags in the 0-63 range.
