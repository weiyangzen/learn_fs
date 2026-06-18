# sources/distributed-fs/ceph-client/samples/hung_task/hung_task_tests.c

Purpose: debugfs sample for provoking hung-task diagnostics using mutex, semaphore, and rwsem contention.

Important APIs/functions: `debugfs_create_dir`, `debugfs_create_file`, `debugfs_remove_recursive`, `DEFINE_MUTEX`, `DEFINE_SEMAPHORE`, `DECLARE_RWSEM`, `guard(mutex)`, `down/up`, `down_read/up_read`, `down_write/up_write`, `msleep_interruptible`, and `simple_read_from_buffer`.

Control flow: init creates `/sys/kernel/debug/hung_task/` files. Reading each file acquires the corresponding lock, sleeps for 256 seconds, and returns dummy data. Multiple readers create lock wait scenarios for hung task reports. Exit removes debugfs entries.

State and persistence: static locks and debugfs dentries while loaded.

Dependencies and integration: debugfs and hung task detector configuration.

Risks: explicitly can freeze or panic test systems depending on hung task settings. Long sleeps under locks are deliberate and should not run on production systems.

Test signals: load in a test VM, read a debugfs file from two processes, and verify hung-task output references the tested lock class.
