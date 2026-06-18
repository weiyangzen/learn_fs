# sources/control-plane/ceph-csi/internal/csi-common/server.go

Purpose: non-blocking standard CSI gRPC server wrapper for identity, controller, node, group controller, and snapshot metadata services.

Important APIs/types/functions: `NonBlockingGRPCServer` interface, `Servers` service bundle, `NewNonBlockingGRPCServer()`, and `nonBlockingGRPCServer` methods `Start()`, `Wait()`, `Stop()`, `ForceStop()`, and `serve()`.

Control flow: `Start()` launches `serve()` in a goroutine and increments a wait group. `serve()` parses `unix://` or `tcp://` endpoints, removes stale Unix socket paths, listens, creates a gRPC server with unary and stream middleware, registers non-nil CSI services, then blocks in `Serve()`. Stop methods call graceful or forceful gRPC stop.

State and persistence: process state includes the gRPC server pointer and wait group. Filesystem state includes Unix socket cleanup and listener. No request state is persisted.

Dependencies and integration points: shared by Ceph-CSI driver binaries. Uses common middleware, CSI protobuf registrations, net/os, gRPC, klog fatal exits, and logging.

Risks: `serve()` calls `klog.Fatal/Fatalf` on parse/listen/serve errors, exiting the process. The server pointer is assigned only inside `serve()` after listener setup; calling stop too early could race with nil pointer. Unix endpoint handling prepends `/` to parsed address, matching existing endpoint format assumptions.

Test signals: no direct tests in this item. Endpoint parsing is tested through utils; server lifecycle would need integration tests with temporary sockets.
