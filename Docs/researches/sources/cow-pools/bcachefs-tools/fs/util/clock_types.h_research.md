# File Research: sources/cow-pools/bcachefs-tools/fs/util/clock_types.h

Defines IO-clock types. Timers contain callback, secondary debug/function pointer, and expiration sector. `io_clock` stores atomic current time, per-CPU sector buffer, max slop, timer spinlock, and min heap. Constants set timer capacity to three per member device and per-CPU buffering to 128 sectors.
