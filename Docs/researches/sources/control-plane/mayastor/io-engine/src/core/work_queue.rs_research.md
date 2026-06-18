# sources/control-plane/mayastor/io-engine/src/core/work_queue.rs

## Purpose
Defines a simple thread-safe FIFO-like work queue abstraction over `crossbeam::queue::SegQueue`.

## Important APIs, Types, and Functions
- `WorkQueue<T: Send + Debug + Display>` stores an incoming `SegQueue<T>`.
- `new`, `enqueue`, `len`, `is_empty`, and `take` expose queue operations.

## Control Flow and State
Producers call `enqueue`, which logs and pushes onto the lock-free queue. Consumers call `take`, which pops one item if available. Length and emptiness are snapshots of the concurrent queue.

State is in-memory queued work only. No persistence or retry metadata exists.

## Dependencies and Integration Points
Used by `device_monitor.rs` for device commands. Could be reused by other core monitor loops.

## Risks and Test Signals
`SegQueue` is unbounded, so producers can outpace consumers. `len` under concurrency is only advisory. Tests should cover enqueue/take order expectations, empty behavior, and concurrent producers/consumers.
