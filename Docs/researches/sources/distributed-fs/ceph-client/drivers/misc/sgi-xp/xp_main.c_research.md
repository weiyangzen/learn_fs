# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xp_main.c

Purpose: implements the XP base module, exports cross-partition service hooks and channel registration state, and decouples XP clients from the XPC module's load state.

Important APIs/functions: exports `xp`, `xp_max_npartitions`, `xp_partition_id`, `xp_region_size`, architecture function pointers, `xpc_registrations`, and `xpc_interface`. `xpc_set_interface()` and `xpc_clear_interface()` are called by XPC load/unload. `xpc_connect()` registers a channel; `xpc_disconnect()` unregisters a channel and asks XPC to tear down active connections.

Control flow: module init initializes registration mutexes and calls `xp_init_uv()` on UV systems. Client registration validates payload sizing and channel parameters, records registration fields under the channel mutex, and triggers `xpc_interface.connect()` if available. Disconnect clears the registration under the mutex and then invokes `xpc_interface.disconnect()`.

State and persistence: all state is module-global and volatile. The XP interface table is zero when XPC is not loaded. Registrations persist while XP remains loaded, allowing XPC to connect newly active partitions after registration.

Dependencies and integration: depends on `xp.h` and UV backend initialization. XPC depends on XP by calling `xpc_set_interface()` and reading `xpc_registrations[]`. XP clients depend only on this base layer and receive `xpNotLoaded` when XPC dispatch is absent.

Risks: disconnect invokes the XPC disconnect hook while holding the registration mutex, so XPC paths must avoid deadlocks with registration operations. Interface pointer updates are simple assignments/zeroing and depend on module lifecycle ordering. `DBUG_ON()` compiles to no-op unless debug mode is enabled, so production validation relies on explicit returns.

Test signals: module init on UV/non-UV, registration success/failure cases, duplicate registration, oversized payload rejection, XPC absent send behavior, and unload sequencing with registered channels.
