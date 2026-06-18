# sources/distributed-fs/ceph-client/drivers/md/dm-stripe.c

## Purpose
Implements the `striped` DM target, mapping logical sectors across multiple devices in fixed-size chunks with support for flush/discard/secure-erase/write-zeroes fan-out, DAX, status reporting, and error events.

## Important APIs, Types, And Functions
`struct stripe` stores a device, physical start, and error counter. `struct stripe_c` stores stripe count, shift optimizations, stripe width, chunk size, target pointer, event work, and flexible stripe array. Important functions are `stripe_ctr()`, `stripe_map()`, `stripe_map_sector()`, `stripe_map_range()`, `stripe_end_io()`, `stripe_status()`, `stripe_iterate_devices()`, and `stripe_io_hints()`.

## Control Flow
Constructor validates stripe count, chunk size, divisibility, device/offset pairs, max IO length, and per-operation bio fan-out. Normal IO computes chunk, stripe, and per-device sector. Flushes use target bio number to select a stripe. Discard/secure erase/write zeroes map only the request range belonging to the selected stripe. End-IO increments per-stripe error counters and queues table events below the threshold.

## State And Persistence
State is in-memory target configuration and error counters. No metadata is persisted, and errors only affect status/event reporting.

## Dependencies And Integration Points
Depends on DM target APIs, block remapping, queue-limit hints, workqueues, DAX, and target registration through `dm_stripe_init()`/`dm_stripe_exit()`.

## Risks
Mapping arithmetic must handle power-of-two and non-power-of-two values correctly. Range operations must not send sectors to the wrong stripe. Event work must be flushed before freeing context. DAX assumes valid lower-device DAX support.

## Test Signals
Verify reads/writes across stripe boundaries, non-power-of-two stripe/chunk cases, flush and discard fan-out, injected IO errors and status flags, DAX operations, and queue hints for `io_min`, `io_opt`, and discard limits.
