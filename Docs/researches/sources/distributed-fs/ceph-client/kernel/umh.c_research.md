<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/umh.c -->
# sources/distributed-fs/ceph-client/kernel/umh.c

Purpose: implements the kernel usermode-helper facility used to spawn userspace programs from kernel context. It handles setup, credential preparation, wait modes, freezer/suspend disablement, running-helper accounting, static-helper disabling, and capability bounding sysctls.

Important APIs and state: public APIs are `call_usermodehelper_setup()`, `call_usermodehelper_exec()`, and `call_usermodehelper()`. Disable/locking APIs include `usermodehelper_read_trylock()`, `usermodehelper_read_lock_wait()`, `usermodehelper_read_unlock()`, `__usermodehelper_set_disable_depth()`, and `__usermodehelper_disable()`. Global state includes capability masks, `umhelper_sem`, `usermodehelper_disabled`, `running_helpers`, and waitqueues.

Control flow: setup allocates `subprocess_info`, initializes work, stores argv/envp/init/cleanup, and optionally replaces the path with `CONFIG_STATIC_USERMODEHELPER_PATH`. Exec rejects invalid paths or disabled state, handles an empty static path as a no-op, queues work to `system_unbound_wq`, and waits according to `UMH_NO_WAIT`, `UMH_WAIT_EXEC`, `UMH_WAIT_PROC`, `UMH_KILLABLE`, and `UMH_FREEZABLE`. Worker context creates a user-mode thread, prepares kernel creds, intersects capability masks, calls optional init, waits for initramfs, and executes the program.

State and persistence: helper lifetime is carried by `subprocess_info`; completion ownership uses `xchg()` to handle killable waiters and no-wait callers. Running-helper counts gate suspend/disable. Sysctls persist capability masks in memory.

Dependencies and integration: depends on workqueues, user-mode thread creation, credentials, freezer, initramfs, kernel execve, sysctl, and module trace events.

Risks: completion ownership is delicate; callers must not use `sub_info` after `UMH_NO_WAIT`. Disable depth races are controlled by rwsem and atomic helper counts. Capability sysctls only drop bits and require strong capabilities. Test signals include no-wait and wait-proc helpers, killable interruption, static helper empty path, suspend disable timeout, cleanup callbacks, and sysctl capability mask writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/umh.c -->
