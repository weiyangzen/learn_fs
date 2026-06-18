# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xp.h

Purpose: defines the public XP/XPC interface used by kernel-level cross-partition clients. It provides partition/channel limits, message size constraints, status codes, callback signatures, registration records, exported interface wrappers, and architecture hooks.

Important APIs/types: `enum xp_retval` is the central status/reason code set. Callback types are `xpc_channel_func` and `xpc_notify_func`. `struct xpc_registration` stores per-channel client registration. `struct xpc_interface` is the runtime dispatch table populated by XPC. Public functions are `xpc_connect()`, `xpc_disconnect()`, `xpc_send()`, `xpc_send_notify()`, `xpc_received()`, and `xpc_partid_to_nasids()`.

Control flow: clients register a channel with message size, queue depth, kthread limits, and a channel callback. XP stores the registration and, if XPC is loaded, asks XPC to connect. Sends go through inline wrappers that return `xpNotLoaded` when XPC has not installed its interface. Received payloads must be acknowledged with `xpc_received()`.

State and persistence: global exported state includes local partition identity, maximum partitions, region size, architecture function pointers, `xpc_registrations[]`, and `xpc_interface`. All are volatile module state.

Dependencies and integration: includes UV headers when configured and is shared by XP base, XPC, and clients such as xpnet. The message sizing macro aligns differently on UV versus non-UV systems and enforces the 128-byte maximum.

Risks: callback functions have strict context requirements; notify callbacks must not block. Registration limits (`assigned_limit`, `idle_limit`) directly affect kthread fan-out. The enum is append-sensitive because values are externally meaningful as callout reasons. Inline wrappers rely on interface pointer consistency during module unload.

Test signals: validate payload size rejection, duplicate registration, disconnect wait semantics, send behavior before XPC load, callback reason propagation, and correct `xp_retval` mapping under partition/channel failures.
