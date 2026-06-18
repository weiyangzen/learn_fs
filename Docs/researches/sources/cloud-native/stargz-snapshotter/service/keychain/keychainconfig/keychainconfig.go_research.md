<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/keychainconfig/keychainconfig.go -->
# sources/cloud-native/stargz-snapshotter/service/keychain/keychainconfig/keychainconfig.go

## Purpose
Assembles resolver credential providers from Docker config, Kubernetes secrets, and CRI PullImage auth for consumers that already own a gRPC server.

## Important APIs, Types, And Functions
- `Config` contains booleans for kube/CRI keychains plus kubeconfig and CRI image service addresses.
- `ConfigKeychain(ctx, rpc, config)` returns ordered credential functions and registers a CRI image service proxy when enabled.
- `newCRIConn` creates a gRPC client with containerd dialer, insecure transport, bounded backoff, and default max message sizes.

## Control Flow
The function always starts with Docker config credentials. It conditionally appends kubeconfig credentials, then conditionally creates a backend CRI client factory, registers the proxy server on `rpc`, and appends CRI credentials.

## State And Persistence
This file stores no state itself. It wires in-memory CRI auth state and kubeconfig secret cache from the keychain implementations.

## Dependencies And Integration Points
Integrates `dockerconfig`, `kubeconfig`, `cri`, containerd defaults/dialer, gRPC, and CRI API registration. It is a reusable alternative to the full containerd plugin core.

## Risks And Edge Cases
`ConfigKeychain` assumes `config` and `rpc` are non-nil. Enabling CRI without a usable address registers a proxy that may never initialize. Credential order means Docker config wins over kube/CRI when it returns non-empty credentials.

## Test Signals
Tests should validate provider ordering, conditional registration, backend address override, gRPC dial options, and CRI credential availability after a proxied PullImage.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/keychainconfig/keychainconfig.go -->
