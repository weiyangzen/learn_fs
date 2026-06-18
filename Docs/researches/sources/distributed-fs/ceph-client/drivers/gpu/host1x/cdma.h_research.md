<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/cdma.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/cdma.h

## Purpose

`cdma.h` defines the generic host1x command-DMA data structures and submission API shared by channel, hardware, timeout, and debug code.

## Important APIs, Types, And Functions

- `struct push_buffer`: mapped WC pushbuffer memory, DMA/physical addresses, circular `fence` and `pos`, and allocation sizes.
- `struct buffer_timeout`: delayed-work state plus the syncpoint/client expected to complete.
- `enum cdma_event`: wait reasons for an empty sync queue or pushbuffer space.
- `struct host1x_cdma`: lock, completion, event state, slot accounting, pushbuffer, FIFO `sync_queue`, timeout, running/teardown flags, and update work.
- Public APIs cover init/deinit, begin/push/push_wide/end, async update, waiting, timeout sync-queue repair, and debug peeking.

## Control Flow

The header documents the producer sequence `begin -> push -> end` and consumer `update` path. Implementations require callers to hold the CDMA lock for waits and most slot/cursor mutations.

## State And Persistence Behavior

The structures are embedded in `struct host1x_channel` and persist for the channel lifetime. Queued jobs and pushbuffer slots persist until syncpoint completion or timeout cancellation retires them.

## Dependencies And Integration Points

It depends on Linux mutex/completion/list/workqueue primitives and is included by `channel.h`, `cdma.c`, `cdma_hw.c`, and debug code. Container macros connect CDMA to its channel and host controller.

## Risks And Test Signals

Field invariants are cross-file contracts: `first_get`, `last_pos`, and `num_slots` must stay in units expected by hardware register code and debug decoding. Build tests catch signature drift; runtime tests should exercise wraparound, timeout, and channel release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/cdma.h -->
