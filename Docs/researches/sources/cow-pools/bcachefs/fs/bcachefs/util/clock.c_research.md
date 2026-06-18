# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/clock.c

This file implements bcachefs I/O clocks: approximate clocks advanced in sectors of I/O, plus timers that fire when the I/O clock reaches a sector count.

Main components:
- Timer ordering uses Linux `min_heap` over `struct io_timer *`, sorted by `expire`.
- `bch2_io_timer_add()`:
  - immediately fires timers already expired
  - avoids duplicate timer insertion
  - pushes future timers into the heap
- `bch2_io_timer_del()` removes a timer from the heap.
- `bch2_io_clock_schedule_timeout()` blocks the current task until an I/O-clock deadline.
- `bch2_kthread_io_clock_wait_once()` and `bch2_kthread_io_clock_wait()` combine I/O-clock waits with CPU-time `schedule_timeout()`, freezer handling, and kthread stop checks.
- `__bch2_increment_clock()` advances the atomic clock and fires all expired timers.
- `bch2_io_timers_to_text()` prints current clock and pending timers.
- `bch2_io_clock_init()` allocates per-CPU buffers and initializes the timer heap.
- `bch2_io_clock_exit()` frees timer heap and per-CPU buffers.

Important invariants:
- Timer heap is protected by `timer_lock`.
- Timers are fired while holding `timer_lock` in `__bch2_increment_clock()`; callbacks must be suitable for that context.
- Clock units are sectors, not wall-clock time.
- Per-CPU batching makes the clock approximate.

Research notes:
- The API is useful for throttling or scheduling based on I/O progress rather than time.
