<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backend/remote/remote.go -->
## sources/control-plane/longhorn-engine/pkg/backend/remote/remote.go

Purpose: remote replica backend implementation that combines gRPC control-plane calls with a dataconn data-plane client.

Important APIs/types/functions: `Remote` holds the data path (`types.ReaderWriterUnmapperAt`), replica service URL, monitor/close channels, and volume name. Control methods include `open`, `Close`, `Snapshot`, `Expand`, `SetRevisionCounter`, metadata getters through `info`, `SetUnmapMarkSnapChainRemoved`, `ResetRebuild`, snapshot limit setters, and `StopMonitoring`. `Factory.Create` resolves control/data addresses, validates the replica is closed, opens multiple data connections, wraps them in `dataconn.Client`, calls `ReplicaOpen`, and starts ping monitoring. `connect` supports TCP and Unix sockets. `monitorPing` periodically sends dataconn pings.

Control flow: each control operation creates a short-lived gRPC client with insecure credentials and identity-validation interceptor, applies a timeout from replica client constants, invokes the replica service RPC, and closes the connection. Data I/O is delegated to `dataconn.Client`. Ping failures set a client error and publish on monitor channel.

State and persistence: does not persist locally; all durable state is in the remote replica. Holds live sockets and goroutines. `Close` closes dataconn and calls `ReplicaClose`.

Dependencies and integration points: integrates with `enginerpc.ReplicaService`, identity interceptors, address utilities, `dataconn`, and `pkg/replica/client` conversion helpers. It is the controller's normal TCP/Unix replica backend.

Risks: frequent one-shot gRPC connections add overhead but isolate calls. Insecure transport relies on trusted environment plus identity validation. Create validates initial state must be closed, so lifecycle mismatches fail add/start. Monitor semantics intentionally do not mark ERR merely because no ping response arrives within interval; data timeout and TCP keepalive are part of failure detection. Review visible duplicate/extra statements in this file should be validated by `go test`/`go test ./pkg/backend/remote` if this tree is expected to compile.

Test signals: controller start/add-replica integration tests, replica service gRPC tests, dataconn timeout tests, and monitor failure tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/backend/remote/remote.go -->
