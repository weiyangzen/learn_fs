# sources/control-plane/external-snapshotter/pkg/webhook/webhook.go

Purpose: starts the HTTPS conversion webhook server and wires readiness, conversion, TLS configuration, and certificate watching.

Important APIs/functions: `StartServer`.

Control flow: starts the `CertWatcher` in a goroutine, registers `/readyz` and `/convert` handlers, builds an `http.Server` with read/write/idle timeouts, creates a TLS listener on the requested port, and serves until listener/server failure.

State and persistence: server state is in-memory; certificate state comes from `CertWatcher`. No graceful shutdown call is wired beyond watcher context cancellation.

Dependencies and integration: integrates `net/http`, `crypto/tls`, klog, conversion framework `serve`, and dynamic TLS reload from `CertWatcher`.

Risks and test signals: risks include `Serve` returning an error after context cancellation being treated by caller as failure, fixed port binding issues in tests, and readiness not validating certificate/conversion health. `webhook_test.go` exercises startup and cert reload through this function.
