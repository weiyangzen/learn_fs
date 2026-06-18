# sources/control-plane/longhorn-engine/pkg/replica/rpc/dataserver.go

Purpose: exposes replica data IO over Longhorn's dataconn protocol on either TCP or Unix-domain sockets.

Important APIs/types/functions: `DataServer` stores protocol, address, and replica `Server`. `NewDataServer` constructs it. `ListenAndServe` dispatches to `listenAndServeTCP` or `listenAndServeUNIX`. Each listener accepts connections and wraps them in `dataconn.NewServer(conn, s.s)`.

Control flow: listeners run infinite accept loops. Each accepted connection is handled in a goroutine with deferred close. EOF from a remote/local close is logged at info and treated as normal; other dataconn errors are warnings.

State and persistence: no durable state. It exposes the underlying replica server's persistent IO operations.

Dependencies and integration points: integrates `dataconn.Server`, `replica.Server`, and `types.DataServerProtocol`. This is the data-plane peer for engine/controller replica IO.

Risks: listeners are never closed by this type and accept loops have no context cancellation. Unix sockets are not unlinked here. There is no backoff on repeated accept errors. TCP listener accepts any peer at the bound address; authentication/encryption is outside this protocol.

Test signals: no direct tests in this file. Network lifecycle and dataconn error behavior require integration tests.
