## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpc-clnt.h

Purpose: declares the RPC client public contract and core client-side data structures.

Important types: `rpc_clnt_event_t` defines connect, disconnect, ping, message, and destroy notifications. `rpc_clnt_status_t` tracks initialized/connected/disconnected connection state. `saved_frame` and `saved_frames` track outstanding requests by XID, including a separate lock-FOP list. `rpc_clnt_prog_t` describes outbound RPC programs. `rpcclnt_cb_program_t` and `rpcclnt_cb_actor_t` describe server-initiated callbacks to the client. `rpc_auth_data_t`, `rpc_clnt_config`, `rpc_clnt_connection_t`, `rpc_req`, and `rpc_clnt_t` hold auth, configuration, transport, request, pool, timer, and owner state.

Important APIs: declares client creation/start/restart, notify registration, request submission, ref/unref, connection cleanup/reconnect cleanup/status, reconfig, callback program registration, disable, and management portmap signout.

Control flow: no implementation, but comments describe response-buffer preconditions for `rpc_clnt_submit`. The types show the intended lifecycle: a client owns a connection, transport, saved frames, request pools, callback program list, context, owner translator, and refcount.

State and persistence: this header defines in-memory state only. Fields such as `xid`, `auth_value`, timers, `last_sent`, `last_received`, `cleanup_gen`, and counters are mutated by implementation files.

Dependencies and integration: includes `rpc-transport.h`, timers, XDR common headers, and GlusterFS protocol definitions. It is the central include for client translators and management helpers.

Risks: struct fields are exposed, so external code may depend on layout or mutate internals. Locking expectations are not encoded in the type system. Callback and frame ownership conventions must match `rpc-clnt.c`.

Test signals: ABI/header compile tests, request submission integration tests, and race tests around exposed connection fields.
