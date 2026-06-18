## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpc-transport.h

Purpose: declares the RPC transport abstraction, event model, message containers, plugin operation table, and transport helper APIs.

Important types and macros: record-marking macros `RPC_LASTFRAG` and `RPC_FRAGSIZE` interpret ONC RPC fragment headers. `peer_info_t` stores op-version bounds, socket address, identifier, and volume name. `rpc_transport_event_t` enumerates accept, disconnect, cleanup, XID mapping, message received/sent, connect, and poller death events. Message structs define request/reply iovec and iobref layouts. `rpc_request_info_t` maps XIDs back to RPC request metadata. `rpc_transport_t` exposes plugin ops, listener, private pointers, locks, refs, context, options, peer state, counters, dynamic handle, SSL/DNS fields, DRC client, and disconnect flags. `rpc_transport_ops` is the plugin vtable.

Important APIs: declarations cover load, ref/unref, listen/connect/disconnect, submit request/reply, notify registration/dispatch, peer lookup, throttling, pollin allocation/destruction, and option builders.

Control flow: no implementation, but the event and vtable definitions define how plugin transports report activity to RPC client/server layers.

State and persistence: header-defined state is per transport and in memory only. Peer identity and counters are runtime diagnostics/control data.

Dependencies and integration: includes RPC system headers, dict/compat/async, and `rpcsvc-common.h`. It is consumed by transport plugins, RPC clients, RPC services, and DRC code.

Risks: public struct exposure means plugin and core code can rely on layout. Fixed-size arrays (`identifier`, `volname`, pollin vectors) require bounded writes. Event enum changes affect plugin/core compatibility.

Test signals: plugin ABI compile tests, record fragment macro tests, pollin vector boundary tests, and event dispatch integration tests.
