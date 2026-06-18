# sources/control-plane/longhorn-engine/pkg/frontend/socket/frontend.go

Purpose: implements a Unix-domain-socket frontend for Longhorn data IO. It creates `/var/run/longhorn-<volume>.sock`, accepts clients, and handles dataconn requests against a `ReaderWriterUnmapperAt` backend.

Important APIs/types/functions: `Socket` tracks volume metadata, `isUp`, socket path, and a `dataconn.Server` pointer. It implements frontend methods `Init`, `Startup`, `Shutdown`, `State`, `Endpoint`, `Upgrade`, and `Expand`. `GetSocketPath` builds the socket path. `startSocketServer` prepares the directory and removes a stale socket. `startSocketServerListen` accepts Unix connections forever. `handleServerConnection` creates a dataconn server per connection. `DataProcessorWrapper` adapts `ReaderWriterUnmapperAt` to `types.DataProcessor` and makes ping a no-op success.

Control flow: `Startup` launches the listener in a goroutine and immediately marks the frontend up. Each accepted connection runs in its own goroutine until dataconn `Handle` returns. `Shutdown` calls `Stop` on `t.socketServer` if set, but the field is never assigned by the listener path, so active per-connection servers are not centrally stopped.

State and persistence: no persistent state. It creates/removes the Unix socket path at startup. Backend mutations persist through the supplied backend.

Dependencies and integration points: uses `dataconn.Server`, `types.ReaderWriterUnmapperAt`, and filesystem/network primitives. It is embedded by the tgt frontend as the local data path backing a Longhorn iSCSI device.

Risks: `GetSocketPath` panics if called before volume initialization. The accept loop has no shutdown condition and continues logging accept errors. `Shutdown` does not close the listener or unlink the socket. `t.socketServer` does not represent per-connection servers, so stop behavior is incomplete. Upgrade and expand are unsupported at this layer.

Test signals: no direct tests. Lifecycle tests should check stale socket removal, listener shutdown, and dataconn ping/read/write/unmap behavior.
