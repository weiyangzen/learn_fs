# sources/control-plane/csi-driver-nfs/pkg/nfs/server.go

Purpose: provides a small non-blocking gRPC server wrapper for registering and serving CSI identity, controller, and node services.

Important APIs and types: `NonBlockingGRPCServer`, `NewNonBlockingGRPCServer`, `nonBlockingGRPCServer.Start`, `Wait`, `Stop`, `ForceStop`, and `serve`.

Control flow: `Start` increments a wait group and launches `serve` in a goroutine. `serve` parses the endpoint, removes stale Unix sockets, listens, creates a gRPC server with the `logGRPC` unary interceptor, conditionally registers provided CSI services, and calls `Serve`. In test mode it marks startup complete and schedules a graceful stop after a short delay so tests do not block forever.

State and persistence behavior: holds the active `*grpc.Server` and wait group in memory. It may delete a Unix-domain socket path before listening.

Dependencies and integration points: depends on `ParseEndpoint`, `logGRPC`, CSI registration functions, `net`, `os`, `sync`, `time`, gRPC, and klog. Called by `Driver.Run`.

Risks: failures call `klog.Fatal/Fatalf`, terminating the process rather than returning errors. `Stop`/`ForceStop` assume `server` has been initialized. Test-mode wait-group handling is subtle because it uses the same wait group for startup and final wait.

Test signals: indirectly smoke-tested by `TestRun`; no dedicated tests cover Unix socket cleanup, listener failures, or stop ordering.
