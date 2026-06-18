## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpc-transport.c

Purpose: implements the generic RPC transport abstraction. It loads transport plugins dynamically, wraps transport operations, manages transport refs and cleanup, allocates incoming message containers, and builds common socket transport option dictionaries.

Important APIs: `rpc_transport_load` normalizes options, opens `$(RPC_TRANSPORTDIR)/<type>.so`, resolves `tops`, `init`, `fini`, optional `reconfigure`, validates transport options, initializes the plugin, and returns a transport. Wrapper APIs include `rpc_transport_submit_request`, `submit_reply`, `connect`, `listen`, `disconnect`, `notify`, `register_notify`, peer address/name helpers, `throttle`, `ref`, `unref`, and pollin alloc/destroy. Option helpers include `rpc_transport_keepalive_options_set`, `rpc_transport_unix_options_build`, and `rpc_transport_inet_options_build`.

Control flow: load allocates a transport, defaults missing `transport-type` to socket, maps legacy `tcp`, `unix`, and `ib-sdp` to socket plus address-family settings, parses insecure bind options, builds the shared-object path, loads symbols, attaches plugin options to `THIS->volume_options` for validation, refs the options dict, initializes locks and plugin state, and returns the live object. Unref triggers cleanup notification, plugin fini, dict unrefs, dlclose, DNS cache cleanup, and free.

State and persistence: transport state is in memory: plugin ops/private data, peer info, options, counters, refs, notify callback, outstanding count, disconnect state, SSL name, DNS cache, and DRC client pointer. No persistent storage.

Dependencies and integration: depends on dynamic loading, dictionaries, xlator `THIS`, libglusterfs iobuf/iobref, rpcsvc common types, and transport plugins exporting expected symbols. It is used by both `rpc-clnt.c` and server-side RPC service code.

Risks: plugin ABI mismatches cause runtime load failures. Option normalization mutates the caller's dict. `THIS` must be valid when validating plugin options. There are two cleanup helpers (`rpc_transport_cleanup` for failed load and `rpc_transport_destroy` for refcounted lifetime) with overlapping responsibilities, so ownership changes must be handled carefully. `rpc_transport_pollin_alloc` copies vectors into a fixed `MAX_IOVEC` array without an explicit count guard in this function.

Test signals: dynamic loading tests for socket/unix aliases, bad plugin symbol tests, option validation, ref/unref cleanup with notify, pollin ref ownership tests, and end-to-end client/server transport round trips.
