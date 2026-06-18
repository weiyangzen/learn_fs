# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_readq.h

Purpose: defines the OSS read queue structure and exported queue operations.

Important APIs and types: `struct seq_oss_readq` stores a `union evrec` ring, length/capacity/head/tail, pre-event timeout, last input timestamp, wait queue, and spinlock. It declares allocation, deletion, clear, poll, enqueue, sysex, timestamp, pick, wait, and free operations plus lock/unlock macros.

Control flow: file read code uses lock/pick/free; producer paths call put functions; ioctl and proc paths inspect queue state.

State and persistence: header-only state description for per-open queues; no globals.

Dependencies and integration: depends on `seq_oss_device.h` and the `union evrec` type from `seq_oss_event.h` through implementation include order.

Risks: callers must hold the queue lock around `pick()` and `free()` according to the contract. The queue exposes integer `qlen`, so non-locked readers should not treat it as stable.

Test signals: static compile coverage and runtime readq producer/consumer tests that enforce lock discipline and queue wraparound.
