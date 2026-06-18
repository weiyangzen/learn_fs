# sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-hw-consumer.c

## Purpose
This file implements the IIO hardware consumer helper, used when an IIO provider is directly connected in hardware to another device and buffers represent hardware data paths rather than CPU-readable storage.

## Important APIs, Types, And Functions
`struct iio_hw_consumer` stores all acquired channels and a list of per-provider hardware buffers. `struct hw_consumer_buffer` embeds an IIO buffer and scan mask for one provider `iio_dev`. `iio_hw_consumer_alloc()` acquires all channels for a device and groups them by provider, setting scan-mask bits. `iio_hw_consumer_enable()` and `iio_hw_consumer_disable()` attach/detach all provider buffers through `iio_update_buffers()`. Devm and manual free helpers are exported.

## Control Flow
A consumer allocates the hardware consumer, enables it when the downstream hardware path should run, disables it when done, then frees it. Enable rolls back already-enabled buffers if a later provider fails.

## State And Persistence
All state is memory-only. Each hardware buffer is reference-counted through the IIO buffer core and contains only access methods, provider pointer, and scan mask. No data is stored by the helper.

## Dependencies And Integration Points
It uses IIO consumer channel acquisition, IIO buffer core, bitmap scan masks, and hardware buffer mode. Exported GPL symbols support both devm and explicit lifetime management.

## Risks
`iio_hw_consumer_get_buffer()` sets `buffer.access` before `iio_buffer_init()`, and `iio_buffer_init()` behavior must preserve or be compatible with subsequent access assignment assumptions. Allocation unwind uses `iio_buffer_put()` for listed buffers but must not miss scan-mask release through buffer release. Provider grouping depends on `chan->indio_dev` termination semantics from `iio_channel_get_all()`.

## Test Signals
Test multiple channels on one provider, channels spanning multiple providers, enable rollback on second provider failure, devm cleanup, missing channel acquisition, and scan mask correctness.
