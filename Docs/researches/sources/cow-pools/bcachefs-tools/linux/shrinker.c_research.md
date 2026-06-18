# File Research: sources/cow-pools/bcachefs-tools/linux/shrinker.c

## Purpose
Userspace implementation of Linux shrinker registration and background memory-pressure scanning.

## Key Responsibilities
- Allocates, registers, unregisters, and frees `struct shrinker`.
- Maintains a global `shrinker_list` protected by `shrinker_lock`.
- Runs shrinkers when allocation fails or when free memory falls below a target.
- Starts a background `shrinkers` kthread in `linux_shrinkers_init()`.

## Behavior
- Allocation-failure mode scans one eighth of counted objects.
- Periodic mode targets roughly 6 percent physical RAM free, adjusted by swap availability.
- The shutdown destructor is disabled because stopping the shrinker thread was observed to segfault rarely.

## Dependencies
Uses kthreads, mutexes, list APIs, percpu init, block device init, `si_meminfo()`, futex waits, and bcachefs `tools-util.h`.
