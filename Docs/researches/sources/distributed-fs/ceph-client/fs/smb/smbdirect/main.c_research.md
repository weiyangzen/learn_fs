## sources/distributed-fs/ceph-client/fs/smb/smbdirect/main.c

Purpose: Owns SMBDirect module-global state, module initialization, workqueue allocation, RDMA device registration, and teardown.

Important APIs and functions: Defines `struct smbdirect_module_state smbdirect_globals`. `smbdirect_module_init()` allocates the accept, connect, idle, refill, immediate, and cleanup workqueues and calls `smbdirect_devices_init()`. `smbdirect_module_exit()` calls `smbdirect_devices_exit()` and destroys all workqueues. `module_init()`/`module_exit()` register the lifecycle hooks.

Control flow: Init locks the global mutex, allocates workqueues in dependency order, initializes devices, unlocks, and reports loaded. Any allocation/device failure jumps through reverse cleanup labels and logs a critical failure. Exit locks, unregisters devices, destroys workqueues, unlocks, and reports unloaded.

State and persistence: Global state is an in-memory module singleton. Workqueues are stored in `smbdirect_globals.workqueues` and copied into each socket during `smbdirect_socket_init()`. Device list state is initialized by `devices.c`. No persistent state exists.

Dependencies and integration points: Depends on Linux module and workqueue APIs, `internal.h`, and `devices.c`. All socket code assumes this initialization has run before sockets are created.

Risks and edge cases: Workqueue allocation failures must unwind in exact reverse order; null destroy safety is not relied on for the failed allocation itself. The cleanup workqueue uses `WQ_MEM_RECLAIM | WQ_HIGHPRI`, indicating disconnect/destroy paths may run under memory pressure. Any future socket initialization before module init would copy NULL workqueue pointers and fail later.

Test signals: Build/module load-unload smoke tests, forced workqueue allocation failure paths if injectable, RDMA device init failure unwinding, repeated load/unload with device add/remove callbacks, and ensuring all workqueues disappear on unload.
