<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/security.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/security.c

## Purpose
`security.c` is the generic AF_RXRPC security dispatcher. It registers available security classes, selects a security module for client calls/connections and incoming service connections, and looks up server security keys.

## Important APIs, Types, And Functions
Important functions include `rxrpc_init_security()`, `rxrpc_exit_security()`, `rxrpc_security_lookup()`, `rxrpc_init_client_call_security()`, `rxrpc_init_client_conn_security()`, `rxrpc_get_incoming_security()`, and `rxrpc_look_up_server_security()`. The central table is `rxrpc_security_types[]`, populated with no-security, optional RxKAD, and optional YFS RxGK.

## Control Flow
Security init iterates the table and calls each module's `init()`, unwinding prior modules on failure. Client call setup validates the key, scans key tokens, chooses the first supported security module, and records the security index. Client connection setup finds the matching token and, while holding `security_lock`, initializes connection security only if the connection is still unsecured, then transitions it to client-secured state. Incoming service security validates the packet security index and service keyring availability, aborting unsupported or unkeyed secure traffic. Server-key lookup builds a key description from service/security/kvno/enctype, searches the service socket keyring under `services_lock`, validates the key, and returns it referenced.

## State And Persistence
The dispatcher owns no per-call crypto state; it writes selected `call->security`, `call->security_ix`, `conn->security_ix`, connection security state, and returns referenced `struct key` objects. The security table persists for module lifetime.

## Dependencies And Integration Points
It depends on compiled security modules, rxrpc key/keyring types, socket service registration, connection state locks, direct connection abort helpers, and packet header security index fields.

## Risks And Edge Cases
Client keys can contain multiple tokens; unsupported tokens are skipped until a supported one is found. Incoming secure service traffic without a keyring is aborted with module-specific `no_key_abort`. Key description formatting must match server-key preparse conventions for RxKAD and RxGK. Connection state transition is protected against duplicate initialization.

## Test Signals
Cover builds with no RxKAD/RxGK, security table init unwind failures, multi-token client keys, expired/revoked keys, unsupported incoming security indices, missing service keyring aborts, server key lookup by kvno/enctype, and concurrent client connection security initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/security.c -->
