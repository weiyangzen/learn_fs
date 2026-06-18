# sources/distributed-fs/ceph-client/kernel/sched/wait_bit.c

## Purpose

`kernel/sched/wait_bit.c` builds bit- and address-keyed waiting APIs on top of generic wait queues. It supports waiters sleeping until a bit clears, waiting while acquiring a bit lock, waking waiters for a specific `(word, bit)` key, and the related `wait_var_event()` mechanism for arbitrary variable addresses.

## Important APIs, Types, and Functions

The file defines a cacheline-aligned global hash table `bit_wait_table` with 256 wait queues. `bit_waitqueue()` maps an `(unsigned long *word, int bit)` pair to a bucket, and `__var_waitqueue()` maps an arbitrary variable address to a bucket. The key types are `struct wait_bit_key` and `struct wait_bit_queue_entry`, with wake callbacks `wake_bit_function()` and `var_wake_function()`.

Main APIs include `__wait_on_bit()`, `out_of_line_wait_on_bit()`, `out_of_line_wait_on_bit_timeout()`, `__wait_on_bit_lock()`, `out_of_line_wait_on_bit_lock()`, `__wake_up_bit()`, `wake_up_bit()`, `init_wait_var_entry()`, `wake_up_var()`, `bit_wait()`, `bit_wait_io()`, `bit_wait_timeout()`, and `wait_bit_init()`.

## Control Flow

`__wait_on_bit()` repeatedly prepares a non-exclusive wait entry, tests the target bit, and invokes the supplied `wait_bit_action_f` callback while the bit remains set. The loop exits when `test_bit_acquire()` observes the bit clear or when the action returns nonzero, then calls `finish_wait()`.

`__wait_on_bit_lock()` uses exclusive waiting and attempts to acquire the bit with `test_and_set_bit()`. It waits while the bit is already set, runs the action callback if sleeping is needed, and returns success when it changes the bit from clear to set. The barrier behavior of `test_and_set_bit()` is part of the correctness contract, especially when an action returns early and `finish_wait()` may not take the queue lock on the fast path.

Wake-up flow constructs a `wait_bit_key`, checks `waitqueue_active()`, and calls `__wake_up()` for one normal waiter. `wake_bit_function()` filters hash-bucket collisions by matching `flags` and `bit_nr`, and it refuses to wake if the bit is still set. Variable waiting uses the same table with `bit_nr = -1`; `var_wake_function()` matches only the address and sentinel bit.

## State and Persistence

The persistent global state is the fixed wait-queue table initialized by `wait_bit_init()`. Individual waits allocate no persistent heap state; wait entries are stack- or caller-owned. Timeout waits store an absolute `jiffies` deadline in `wq_entry.key.timeout`. Correctness depends on external owners clearing bits or updating variables with release/ordered semantics before calling `wake_up_bit()` or `wake_up_var()`.

## Dependencies and Integration Points

This file depends on generic wait-queue APIs from `wait.c`, bitops, hashing helpers, `jiffies`, signal-pending checks, `schedule()`, `io_schedule()`, and `schedule_timeout()`. It is used by page, buffer, filesystem, block, and driver code that represents lock or readiness state as bits or address-associated conditions.

## Risks and Edge Cases

Hash buckets can contain unrelated waiters, so key matching in wake callbacks is mandatory. Missing memory barriers after clearing a bit or updating a variable can let waiters wake before the condition's data is visible. `wake_up_bit()` comments explicitly require a full barrier unless the clear/update operation is fully ordered. Timeout handling uses absolute `jiffies`, so wrap-safe `time_after_eq()` behavior is important. `__wait_on_bit_lock()` must not lose exclusive waiters when the action returns an error or signal interruption.

## Test Signals

Useful coverage includes clear-and-wake ordering tests on SMP, hash-collision tests with different words and bits, signal-interruptible waits, IO wait accounting through `bit_wait_io()`, timeout expiry and success before timeout, bit-lock acquisition under contention, and `wait_var_event()` wakeups for address-only conditions.
