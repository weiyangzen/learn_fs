# sources/control-plane/juicefs-csi-driver/pkg/driver/driver.go

Purpose: defines the top-level CSI `Driver` that wires identity, controller, node, and provisioner services into one gRPC server.

Important APIs and types: `Driver` embeds `csi.UnimplementedIdentityServer`, `*controllerService`, `nodeService`, and `provisionerService`, and stores the gRPC server plus endpoint. `NewDriver` builds a Kubernetes client unless `config.ByProcess` is set, constructs controller/node/provisioner services, logs build metadata, and returns the assembled driver. `Run` optionally starts the external provisioner controller, parses the endpoint, listens on the endpoint transport, creates a gRPC server with an error-logging unary interceptor, and registers CSI Identity, Controller, and Node servers. `Stop` calls `d.srv.Stop()`.

Control flow: initialization is synchronous and fails fast on Kubernetes client or subservice construction errors. Runtime serving is blocking through `grpc.Server.Serve`; the provisioner runs in a background goroutine only when `config.Provisioner` is true.

State and persistence behavior: the driver itself persists only process-local service objects and server handles. External state is delegated to subservices: Kubernetes API access, mount state, provisioner leader-election leases, and JuiceFS state are not managed directly in this file.

Dependencies and integration points: integrates CSI gRPC registration, Prometheus registerers for subservice metrics, Kubernetes client creation, endpoint parsing from `util.ParseEndpoint`, global configuration, and service constructors in this package.

Risks and test signals: `Stop` assumes `Run` initialized `d.srv`; calling it before a successful `Run` would panic. `Run` uses `context.Background()` for provisioner lifetime, so shutdown coordination depends on process termination rather than a passed context. The constructor logs a misspelled `"verison"` key, which is harmless but visible in logs. Tests cover constructor success and a node-service error path, not real socket serving or provisioner goroutine lifecycle.
