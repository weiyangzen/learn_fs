# File Research: sources/block-storage/kvdo/vdo/thread-cond-var.c

This file implements UDS condition variables using `event_count`. Initialization allocates an event count; signal and broadcast both broadcast to all waiters.

`uds_wait_cond()` and `uds_timed_wait_cond()` prepare an event token, unlock the provided mutex, wait on the event count, then relock the mutex. The timed variant returns `ETIMEDOUT` when the wait expires. `uds_destroy_cond()` frees the event count and clears the pointer.
