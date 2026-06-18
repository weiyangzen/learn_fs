# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/clock_types.h

This header defines I/O clock and timer data structures.

Key definitions:
- `NR_IO_TIMERS` is `BCH_SB_MEMBERS_MAX * 3`.
- `IO_CLOCK_PCPU_SECTORS` is 128, the per-CPU batching threshold.
- `struct io_timer`:
  - callback function
  - secondary function/debug pointer
  - expiration sector
- `io_timer_heap`: min-heap of `struct io_timer *`.
- `struct io_clock`:
  - atomic sector clock
  - per-CPU sector buffer
  - max slop
  - spinlock
  - timer heap

Important behavior:
- Clocks and timers are expressed in sectors of I/O.
- Per-CPU buffering means the clock has bounded imprecision.

Research notes:
- This type header depends on the vendored min-heap implementation and the member-device limit.
