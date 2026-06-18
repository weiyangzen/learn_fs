# sources/distributed-fs/ceph-client/kernel/trace/pid_list.c

## Purpose

`pid_list.c` implements the sparse PID bitmap used by tracing filters such as `set_ftrace_pid` and related trace PID controls. It stores up to 30-bit PIDs in a two-level upper pointer tree plus lower bitmaps, with a small preallocated chunk cache so scheduler-context operations can avoid allocation. Readers use seqcount retry loops, while writers use a raw spinlock and schedule asynchronous cache refills via irq_work.

## Important APIs, Types, and Functions

- Public operations: `trace_pid_list_alloc()`, `trace_pid_list_free()`, `trace_pid_list_is_set()`, `trace_pid_list_set()`, `trace_pid_list_clear()`, `trace_pid_list_first()`, and `trace_pid_list_next()`.
- Addressing helpers: `pid_split()` breaks a PID into `upper1`, `upper2`, and `lower` indexes; `pid_join()` reconstructs a PID for iteration.
- Chunk cache helpers: `get_upper_chunk()`, `get_lower_chunk()`, `put_upper_chunk()`, and `put_lower_chunk()`.
- Refill worker: `pid_list_refill_irq()` allocates replacement chunks with `GFP_NOWAIT` outside the critical scheduler lock path, then splices them into free lists.
- Emptiness helper: `upper_empty()` detects when an upper chunk has no lower chunk pointers and can be recycled.

## Control Flow

Allocation creates a zeroed `trace_pid_list`, initializes `refill_irqwork`, a raw spinlock, and a seqcount associated with that lock, then preallocates `CHUNK_ALLOC` upper and lower chunks into free lists. The implementation warns if `init_pid_ns.pid_max` exceeds the 30-bit design assumption.

Setting a PID validates the PID with `pid_split()`, takes `pid_list->lock` with IRQ save, starts a seqcount write section, obtains or allocates the needed upper and lower chunks from free lists, sets the lower bitmap bit, ends the seqcount write section, and releases the lock. If free chunks fall to `CHUNK_REALLOC` or below, `get_*_chunk()` queues `refill_irqwork` because direct allocation may not be safe while scheduler runqueue locks are held.

Clearing a PID follows the same split and lock path, clears the bit if present, and recycles the lower chunk when its bitmap becomes empty. If the containing upper chunk then has no lower chunks, it is recycled too. Iteration through `trace_pid_list_next()` scans upper1, upper2, and lower bitmap positions under the spinlock and returns the first PID at or after the requested start. `trace_pid_list_first()` is a convenience wrapper starting at zero.

Membership testing is optimized for scheduler hot paths. `trace_pid_list_is_set()` validates the PID, then repeatedly snapshots the relevant pointers and bit under `read_seqcount_begin()`/`read_seqcount_retry()` until no concurrent writer invalidated the read. It avoids taking the raw spinlock on the read side.

Freeing synchronizes pending irq_work, drains free-list chunks, walks all active upper/lower chunks, frees everything, and then frees the list object.

## State and Persistence Behavior

The state is entirely in-memory. `trace_pid_list` contains a 256-entry upper pointer array, two free lists, free counts, lock, seqcount, and irq_work item. Active PID membership lives in lower bitmap chunks. Empty subtrees are returned to the free lists instead of left attached. Free chunk counts are maintained under the raw spinlock, and warnings catch negative counts. No state is persisted outside the owning tracing subsystem.

## Dependencies and Integration Points

The code depends on the layout constants and structures in `pid_list.h`, tracing helpers in `trace.h`, kernel raw spinlocks, seqcount, irq_work, bitmap operations, and slab allocation helpers. It is used by ftrace PID filtering and other trace PID filters to support checks from scheduler switch/fork/exit paths.

## Risks and Edge Cases

- PID validation rejects values `>= MAX_PID`; callers must handle `-EINVAL`.
- If the chunk cache is exhausted, `trace_pid_list_set()` returns `-ENOMEM` instead of allocating directly in a sensitive path.
- `pid_list_refill_irq()` uses `GFP_NOWAIT`; allocation failures stop the current refill attempt and leave future sets dependent on remaining cache.
- Readers rely on seqcount correctness. Any writer that mutates tree pointers without the seqcount would make lockless reads unsafe.
- Iteration uses the raw spinlock and can scan the sparse tree, so very sparse high PID sets may cost more than membership tests.
- Free must call `irq_work_sync()` before releasing memory to avoid use-after-free by pending refill work.

## Test Signals

Direct unit signals are allocation success, set/is_set/clear behavior for low, boundary, and invalid PIDs, first/next iteration ordering, cache refill after more than `CHUNK_ALLOC` sparse insertions, and freeing with pending refill work. Integration signals include ftrace PID tracefs behavior, scheduler switch filtering, and fork/exit propagation of trace PID lists.
