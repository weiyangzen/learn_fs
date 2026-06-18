# File Research: sources/cow-pools/bcachefs-tools/fs/util/clock.h

Declares IO clock/timer functions and provides `bch2_increment_clock()`, which batches sector increments per CPU and flushes to the shared atomic clock when the per-CPU threshold is reached. Exposes timer add/delete, kthread waits, timeout scheduling, diagnostics, init, and exit.
