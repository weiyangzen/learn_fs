# sources/control-plane/mayastor/io-engine/src/core/io_driver.rs

## Purpose
Implements a test/support I/O workload driver that creates or opens a bdev and continuously submits random read or write I/O at a configured queue depth.

## Important APIs, Types, and Functions
- `IoType::{Read, Write}` selects workload direction.
- `Builder` configures URI, queue depth, I/O size, existing bdev, and core.
- `Job` owns the descriptor, I/O channel, queue, counters, RNG, drain/reset flags, and thread.
- `JobQueue` starts/stops jobs, stops all jobs, and signals reset across jobs.

## Control Flow and State
`Builder::build` creates or opens the bdev, computes block and I/O geometry, allocates one `DmaBuf` per queue entry, and returns a `Job`. `Job::start` creates an SPDK thread on the selected core, allocates a channel, boxes the job, and starts each queued `Io`. Each completion frees SPDK I/O, updates inflight/completion counters, sends the drain oneshot if all I/O has drained, otherwise submits another random offset unless draining. Reset requests cause the next I/O to submit a reset first.

State is all in-memory and tied to the created SPDK thread/channel. Created bdevs persist according to their backend until deleted elsewhere.

## Dependencies and Integration Points
Depends on `bdev_create`, `UntypedBdev`, `UntypedDescriptorGuard`, SPDK bdev I/O calls, `DmaBuf`, `Thread`, and `Cores`. Intended for tests and diagnostics rather than production data path.

## Risks and Test Signals
Several calculations can divide by zero if invalid `io_size` or block size reaches the builder. The random offset expression appears to use `rng % io_size` multiplied by `io_blocks`, which may not span the full device as expected. Completion sends the drain signal when inflight reaches zero; double stop panics. Tests should cover build validation, stop/drain, reset injection, core affinity assertion, and qd/io-size edge cases.
