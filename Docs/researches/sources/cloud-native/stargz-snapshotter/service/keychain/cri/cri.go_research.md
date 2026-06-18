<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/cri/cri.go -->
# sources/cloud-native/stargz-snapshotter/service/keychain/cri/cri.go

## Purpose
Implements a CRI image service proxy that records `PullImage` auth configs and exposes them as resolver credentials for lazy snapshot pulls.

## Important APIs, Types, And Functions
- `NewCRIKeychain(ctx, connectCRI)` returns a `resolver.Credential` and a `runtime.ImageServiceServer` proxy.
- `instrumentedService.credentials` looks up auth by normalized image reference and handles Docker Hub host aliases.
- `PullImage` stores request auth before forwarding to the backend CRI service.
- `RemoveImage` deletes stored auth for the image and forwards the request.
- `parseReference` normalizes Docker references through distribution and containerd parsers.

## Control Flow
A background goroutine retries backend CRI connection up to 100 times with 10 second sleeps. Proxy methods fail until a backend client exists. Image operations parse the image reference, mutate the auth map under a mutex when needed, and delegate to the real CRI client.

## State And Persistence
Auth configs are stored only in memory in `map[string]*runtime.AuthConfig`. They persist for the process lifetime until `RemoveImage` or restart.

## Dependencies And Integration Points
Depends on Kubernetes CRI API, containerd reference parsing, and `service/resolver.ParseAuth`. It is registered either by `plugincore` on a Unix socket or by `keychainconfig` on an existing gRPC server.

## Risks And Edge Cases
Credentials are process-memory only and keyed by normalized refs, so alternate tags/digests may not match. Backend connection retry can silently leave the proxy uninitialized. Auth entries can remain if images are never removed.

## Test Signals
Useful tests cover PullImage storing auth, credential lookup for Docker Hub aliases, RemoveImage cleanup, proxy errors before initialization, and parse failures for invalid image refs.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/cri/cri.go -->
