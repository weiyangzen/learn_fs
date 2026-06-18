# sources/distributed-fs/ceph-client/drivers/tty/n_null.c

Purpose: this file implements the minimal `N_NULL` line discipline used as a failure-path placeholder. It accepts registration as a tty ldisc but provides no data transport.

Important APIs and functions: `n_null_read()` and `n_null_write()` both return `-EOPNOTSUPP`. `null_ldisc` sets `.owner`, `.num = N_NULL`, `.name = "n_null"`, `.read`, and `.write`. Module lifecycle is `n_null_init()` registering the ldisc and `n_null_exit()` unregistering it.

Control flow: module init calls `tty_register_ldisc(&null_ldisc)` and uses `BUG_ON()` if registration fails. Once selected, tty read or write attempts immediately fail with operation-not-supported. There are no receive, open, close, poll, ioctl, or buffer callbacks.

State and persistence: there is no per-tty private state, no buffering, no timers, and no persistent state. The only state is global registration of the ldisc with the tty core while the module is loaded.

Dependencies and integration points: depends only on the tty ldisc registration API and standard Linux module infrastructure. It integrates with tty fallback/error handling by providing a named ldisc number that can be installed when a real ldisc cannot be used.

Risks: `BUG_ON()` during module init turns registration failure into a kernel bug rather than a recoverable error, which is consistent with a core fallback discipline but still severe. Because no `.open`/`.close` methods exist, the tty core must not expect private state. Any caller assuming reads/writes behave like `/dev/null` would be wrong; this discipline rejects I/O rather than discarding writes or returning EOF.

Test signals: build and module load/unload, successful registration under `N_NULL`, read and write returning `-EOPNOTSUPP`, and fallback selection paths that install `N_NULL` without dereferencing missing callbacks.
