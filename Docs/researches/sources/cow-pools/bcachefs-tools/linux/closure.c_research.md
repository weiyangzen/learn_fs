# File Research: sources/cow-pools/bcachefs-tools/linux/closure.c

Implements bcachefs closure reference/counting primitives. `closure_sub()` drives state transitions for normal put, requeue, wake sleeping waiters, destructor execution, and parent put. Wait lists use lockless lists and FIFO reversal. Sync helpers sleep through the scheduler shim until closure completion.

Optional debug support tracks live closures and exposes a debugfs file.
