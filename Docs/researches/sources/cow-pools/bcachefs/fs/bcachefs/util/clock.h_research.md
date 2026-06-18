# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/clock.h

This header declares I/O clock APIs and defines the inline fast path for clock advancement.

Exports:
- Timer operations:
  - `bch2_io_timer_add()`
  - `bch2_io_timer_del()`
- Wait operations:
  - `bch2_kthread_io_clock_wait_once()`
  - `bch2_kthread_io_clock_wait()`
  - `bch2_io_clock_schedule_timeout()`
- Clock advancement:
  - `__bch2_increment_clock()`
  - inline `bch2_increment_clock()`
- Diagnostics/lifecycle:
  - `bch2_io_timers_to_text()`
  - `bch2_io_clock_exit()`
  - `bch2_io_clock_init()`

Important behavior:
- `bch2_increment_clock()` accumulates sectors in a per-CPU buffer and only calls the global increment path when the per-CPU threshold is reached.
- It chooses read/write clock by indexing `c->io_clock[rw]`.

Research notes:
- The header keeps the high-frequency per-I/O path inline and defers heap/timer work to `clock.c`.
