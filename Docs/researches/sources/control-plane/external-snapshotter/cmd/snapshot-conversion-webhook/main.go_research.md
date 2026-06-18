# sources/control-plane/external-snapshotter/cmd/snapshot-conversion-webhook/main.go

## Purpose
Main entrypoint for the HTTPS snapshot conversion webhook server.

Source size: 82 lines, 2135 bytes.

## Important APIs, Types, and Functions
- Go package `main`.
- Functions/methods: `main`.
- Key imports: `context`, `crypto/tls`, `flag`, `k8s.io/component-base/logs`, `k8s.io/component-base/logs/api/v1`, `k8s.io/klog/v2`, `github.com/kubernetes-csi/csi-lib-utils/standardflags`, `github.com/kubernetes-csi/external-snapshotter/v8/pkg/webhook`.

## Control Flow
- Parses TLS certificate, private key, and port flags with logging setup.
- Validates required TLS paths, creates a cert watcher, configures `tls.Config.GetCertificate`, and starts the webhook server with a cancellable context.
- The server handles conversion requests through the `pkg/webhook` package.

## State and Persistence
- Maintains process-local TLS watcher and HTTP server state.
- No Kubernetes objects are persisted by this file directly; it serves conversion traffic from the API server.

## Dependencies and Integration Points
- Go TLS/context/flag, component-base logging, csi-lib-utils standardflags, external-snapshotter webhook package.

## Risks and Edge Cases
- Missing or unreadable cert/key files are fatal.
- Webhook Deployment/Service/CA bundle must match the serving cert or API conversion fails.

## Test Signals
- Operational test is API-server conversion through the deployed webhook example.
