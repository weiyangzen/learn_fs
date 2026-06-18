# File Research: sources/cow-pools/bcachefs-tools/linux/wait.c

## Purpose
Userspace implementation of Linux waitqueues, bit waits, and completions.

## Key APIs
- `wake_up()`, `wake_up_all()`
- `prepare_to_wait()`, `finish_wait()`
- `default_wake_function()`, `autoremove_wake_function()`
- `wake_up_bit()`, `__wait_on_bit()`, `out_of_line_wait_on_bit_timeout()`, `__wait_on_bit_lock()`
- `complete()`, `wait_for_completion()`, `wait_for_completion_timeout()`

## Behavior
- Waitqueues are protected by spinlocks and use list entries.
- Exclusive waits are queued at the tail and stop after the requested number of exclusive wakeups.
- Bit waits share one global `bit_wq` and match on `(word, bit_nr)`.
- Completions decrement `done` when consumed.

## Dependencies
Depends on local scheduler, waitqueue, wait-bit, completion, list, bit, and spinlock shims.
