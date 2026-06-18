<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence.h -->
# sources/distributed-fs/ceph-client/include/linux/dma-fence.h

## Purpose
Defines the DMA fence synchronization primitive used to represent asynchronous DMA or hardware work completion across drivers.

## Important APIs, Types, And Functions
Core types are `struct dma_fence`, `struct dma_fence_cb`, and `struct dma_fence_ops`. APIs cover initialization, refcounting, RCU-safe get, locking, signaling, default waits, callbacks, software signaling, driver/timeline names, signaled/status checks, seqno ordering helpers, error setting, timestamp access, waits on one or any fence, deadlines, stub fences, context allocation, and container type checks.

## Control Flow
Drivers initialize a fence with ops, context, and seqno before publishing it. Waiters add callbacks or call wait functions, which may enable software signaling through the implementation. Producers set any error before signaling, then signal with timestamp, waking callbacks and waiters. Consumers compare seqnos only within the same context.

## State And Persistence
A fence stores an ops pointer, callback list until signaling, timestamp after signaling, RCU release state after destruction, context, seqno, flags, refcount, and optional negative error. It is transient synchronization state and can detach driver ops after signaling depending on callbacks.

## Dependencies And Integration Points
Depends on wait queues, spinlocks, krefs, RCU, timekeeping, lockdep, and seq files. It integrates DMA-BUF, DMA reservation objects, GPU schedulers, sync files, and drivers with hardware completion interrupts.

## Risks And Edge Cases
The lifetime contract is strict: external driver data behind ops must not be accessed after signaling unless protected by RCU. `enable_signaling()` can race with immediate signal and should take a reference if hardware interrupt handling needs it. Error must be set before signal. Custom wait/release ops keep modules loaded longer. Sequence comparisons across contexts are invalid, and 32-bit seqno wrap depends on flags.

## Test Signals
Tests should cover callback add/remove, wait timeout and interruptible wait, already signaled fences, error status, timestamp ordering, software-signaling enable races, RCU-safe get, context allocation, seqno wrap, deadline callbacks, stub fences, and lockdep signaling annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma-fence.h -->
