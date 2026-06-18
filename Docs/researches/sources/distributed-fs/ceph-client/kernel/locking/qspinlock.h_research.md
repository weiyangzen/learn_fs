# sources/distributed-fs/ceph-client/kernel/locking/qspinlock.h

## Purpose
Shared internal definitions for queued spinlock slow paths. It defines per-CPU queue node layout, tail encoding/decoding, pending-bit manipulation, tail exchange, and locked-byte setting.

## Important APIs, Types, and Functions
- `struct qnode` embeds `struct mcs_spinlock` and optional PV padding.
- `_Q_MAX_NODES` sets the maximum nesting level to four.
- `encode_tail()` and `decode_tail()` map CPU and nesting index into/from the lock tail bits.
- `grab_mcs_node()` computes the node for a nesting index.
- `clear_pending()`, `clear_pending_set_locked()`, `xchg_tail()`, `queued_fetch_set_pending_acquire()`, and `set_locked()` operate on architecture-specific qspinlock fields.

## Control Flow
This header supplies inline operations used by `qspinlock.c`. There are two implementations of pending/tail operations depending on whether pending bits occupy a byte; byte-capable architectures can write subfields directly, while others update the full atomic word with compare/exchange loops.

## State and Persistence
No independent state besides the qnode layout. It defines how the `qspinlock` word and per-CPU nodes are interpreted.

## Dependencies and Integration Points
Depends on asm-generic qspinlock and MCS spinlock definitions, per-CPU accessors, and architecture qspinlock field layout. Included by both native and paravirtual slow-path generation.

## Risks
Incorrect tail encoding can make CPU 0/index 0 indistinguishable from no-tail, hence the CPU-plus-one encoding. Changing `_Q_PENDING_BITS` behavior affects memory ordering and atomic field updates. `xchg_tail()` uses relaxed semantics because callers must publish fully initialized MCS nodes first.

## Test Signals
Compile on architectures with and without 8-bit pending fields, CPU-count boundary builds, qspinlock torture, and KCSAN/lockdep signals around tail publication and successor wakeups.
