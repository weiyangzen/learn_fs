## sources/control-plane/csi-driver-iscsi/pkg/iscsi/server.go

Purpose: wraps gRPC server startup in a non-blocking interface for CSI services.

Important APIs are `NonBlockingGRPCServer`, `NewNonBlockingGRPCServer`, and methods `Start`, `Wait`, `Stop`, `ForceStop`, and `serve`. Control flow starts serving in a goroutine, parses endpoint, removes existing Unix socket, listens, installs a unary logging interceptor, registers non-nil identity/controller/node servers, and serves until fatal error.

State is a wait group and `*grpc.Server` pointer. Filesystem state includes Unix socket removal/creation. Dependencies are net, os, sync, grpc, CSI generated registration, klog, and `ParseEndpoint`. Risks include `Stop`/`ForceStop` nil panic if called before server assignment, fatal exits inside goroutine, no socket permission management, only unary interceptor, and no graceful handling of `Serve` returning after Stop. Test signal is runtime startup; no direct tests listed.
