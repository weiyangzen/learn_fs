# Research: sources/control-plane/rook/pkg/client/clientset/versioned/clientset.go

Purpose: defines the generated top-level Rook versioned clientset. It exposes `Interface` with `Discovery()` and `CephV1()`, wraps a Kubernetes `DiscoveryClient`, and wires the Ceph v1 typed client into a single object that controller code can construct from a `rest.Config` or existing `rest.Interface`.

Important APIs/types/functions: `Clientset` stores `*discovery.DiscoveryClient` and `*cephv1.CephV1Client`. `NewForConfig` shallow-copies the provided config, fills a default user agent, builds a shared `http.Client`, and delegates to `NewForConfigAndClient`. `NewForConfigAndClient` installs a token-bucket rate limiter when `RateLimiter` is nil and QPS is set, constructs the Ceph v1 client, then constructs discovery. `NewForConfigOrDie` panics on construction errors. `New` adapts a prebuilt REST client.

Control flow: construction is fail-fast. Invalid QPS/Burst settings return an error before any clients are returned. The same HTTP client and config shallow copy are shared by the typed Ceph client and discovery client. Accessor methods just return stored clients, with `Discovery()` nil-safe.

State and persistence behavior: the clientset holds client handles only. It persists nothing locally; all resource state lives in the Kubernetes API server reached through REST clients. Rate limiting state is in the generated limiter when configured.

Dependencies and integration points: depends on `pkg/client/clientset/versioned/typed/ceph.rook.io/v1`, `k8s.io/client-go/discovery`, `k8s.io/client-go/rest`, and `flowcontrol`. Controllers, CLIs, reconcilers, and integration tests use this as the main entry point for Rook Ceph CRD access.

Risks: generator drift or a missing typed client field would make `clientset.Interface` incomplete. Incorrect rate limiter handling could produce unexpected API pressure or construction failures. Passing a nil config would panic because the code dereferences `*c`, which is standard generated-client behavior but still a caller responsibility.

Test signals: package compile tests catch interface conformance. Integration or fake-apiserver tests should verify `NewForConfig`, `NewForConfigAndClient`, and `New(c rest.Interface)` can reach `CephV1()` and discovery with expected REST configuration.
