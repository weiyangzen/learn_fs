# sources/cloud-native/soci-snapshotter/service/keychain/cri/v1/cri.go

Purpose: CRI image-service proxy and credential provider that captures credentials from CRI `PullImage` requests so the snapshotter can authenticate registry access for snapshots.

Important APIs/types/functions: `NewCRIKeychain` returns a `resolver.Credential` function and a `runtime.ImageServiceServer`. `instrumentedService` wraps a backend CRI `ImageServiceClient`, stores auth config per image reference, and implements `ListImages`, `ImageStatus`, `PullImage`, `RemoveImage`, and `ImageFsInfo`. `parseReference` normalizes Docker references into containerd reference specs.

Control flow: `NewCRIKeychain` starts a goroutine retrying backend CRI connection up to 100 times with 10-second sleeps. `PullImage` parses the image reference, stores `AuthConfig`, then forwards to backend CRI. `RemoveImage` deletes stored auth for that image and forwards. `credentials` maps docker.io hosts to `index.docker.io`, looks up auth by full image reference, and delegates parsing to `resolver.ParseAuth`.

State and persistence: in-memory map from image reference string to CRI `AuthConfig`, guarded by mutex. Backend CRI client is also guarded by mutex. State is not persisted across process restart.

Dependencies/integration points: used by `service/plugin` when CRI keychain is enabled. Integrates Kubernetes CRI v1 API, containerd reference parsing, distribution reference normalization, and resolver credential chains.

Risks: credentials are keyed by full image reference, so tag/digest normalization consistency is critical. If backend CRI connection is unavailable, calls fail with "server is not initialized yet". Stored credentials remain until `RemoveImage`; no TTL. Only implemented image-service methods are proxied.

Test signals: no direct tests in this file; integration tests enabling CRI keychain would validate pull authentication behavior.
