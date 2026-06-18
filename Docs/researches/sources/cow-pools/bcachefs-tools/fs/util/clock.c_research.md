# File Research: sources/cow-pools/bcachefs-tools/fs/util/clock.c

Implements approximate IO-sector clocks with min-heap timers. Timers are added under a spinlock, fire immediately if already expired, and are deduplicated before heap insertion. Delete scans the heap and removes matching timers.

Wait helpers schedule the current task until IO-clock expiration or CPU timeout, with kthread stop/freezer awareness. Clock increments add sector deltas to `now`, pop expired timers, and invoke callbacks. Text output prints current time and pending timers; init/exit allocate/free percpu buffers and timer heaps.
