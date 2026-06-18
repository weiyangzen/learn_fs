## sources/distributed-fs/beegfs/client_module/source/program/Main.c

**Purpose:** Defines the BeeGFS kernel client module entry and exit routines, including subsystem initialization, filesystem registration, procfs setup, and cleanup.

**Important APIs/types/functions:** `init_fhgfs_client` is registered with `module_init`; `exit_fhgfs_client` is registered with `module_exit`. The file also declares module license, description, author, alias, and version metadata.

**Control flow:** Initialization uses a fail-label cascade: fault injection, native emergency pools, commkit emergency pools, socket one-time init, inode cache, RWPages workqueue, remoting message buffers, page-list vector cache, filesystem registration, and procfs creation. On any failure it unwinds only the subsystems already initialized. Exit performs the reverse cleanup order and asserts filesystem unregister succeeds.

**State and persistence behavior:** Module load creates kernel caches, pools, workqueues, socket state, procfs entries, and filesystem registration. Unload destroys them. No on-disk state is written here.

**Dependencies and integration points:** Integrates all major client module subsystems: fault injection, native IO, commkit, sockets, inode/page caches, remoting, procfs, and VFS registration.

**Risks:** Initialization order is a contract: later subsystems may assume earlier pools/caches exist. Cleanup labels must remain synchronized with added initialization steps. Returning `-EPERM` for all init failures loses specific error detail. `BUG_ON` during unregister can panic if teardown invariants are violated.

**Test signals:** Test module load/unload, forced failure at each initialization step, double-load prevention through kernel module machinery, procfs creation/removal, filesystem mount after registration, and leak checks for all pools/caches/workqueues.
