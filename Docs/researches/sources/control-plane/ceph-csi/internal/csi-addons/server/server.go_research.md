# sources/control-plane/ceph-csi/internal/csi-addons/server/server.go

Purpose: standalone gRPC server wrapper for CSI-addons services over Unix domain sockets.

Important APIs/types/functions: `ErrNoUDS`, `CSIAddonsService` interface with `RegisterService()`, `CSIAddonsServer` state (`scheme`, `path`, `server`, `services`), `NewCSIAddonsServer()`, `RegisterService()`, `Start()`, `Stop()`, and `serve()`.

Control flow: construction parses an endpoint URL and accepts only `unix://` schemes. Services are appended before `Start()`. Start creates a gRPC server with common unary middleware, registers each addon service, removes any stale socket path, listens on the Unix socket, and serves asynchronously. Stop gracefully stops the gRPC server if started.

State and persistence: process state includes service list and server pointer. Filesystem state includes the Unix domain socket path, which is removed before listening. No service data is persisted here.

Dependencies and integration points: depends on Go net/url/net/os, gRPC, common CSI middleware, and logging. RBD/CephFS addon services register through this wrapper.

Risks: only unary middleware is configured; stream middleware is not used here. Existing socket path removal can delete a stale or incorrectly configured file. Empty endpoint parsing returns a generic parse/scheme error. `Stop()` before `Start()` is safe.

Test signals: tests cover valid Unix endpoints, empty endpoint, and non-UDS endpoint. Additional tests should cover stale socket removal, listen failures, service registration, and graceful stop.
