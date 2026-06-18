# File Research: sources/cow-pools/bcachefs-tools/linux/kthread.c

Implements kernel-thread compatibility using pthreads. `kthread_create()` allocates a `task_struct`, sets flags/state/name, initializes completion/rwsem, and starts a pthread with a small stack. The start wrapper registers RCU/percpu state, waits for wakeup, runs the thread function, completes exit, and unregisters.

`kthread_stop()` sets the stop bit, wakes the task, and waits for exit.
