## sources/cloud-native/buildkit/snapshot/containerd/content.go

Purpose: wraps a containerd content store so all operations run under a fixed namespace, while forbidding direct deletes and optionally falling back to another namespace for reads.

Important APIs/types/functions: `NewContentStore` creates `Store{ns, content.Store}`. `Namespace` and `WithNamespace` expose namespace controls. Store methods `Info`, `Update`, `Walk`, `Status`, `ListStatuses`, `Abort`, `ReaderAt`, and `Writer` inject `namespaces.WithNamespace`. `Delete` returns an error to forbid content deletion. `nsWriter.Commit` also injects namespace. `WithFallbackNS` returns `nsFallbackStore`, whose `Info`, `Walk`, and `ReaderAt` can fall back to a secondary namespace.

Control flow: normal methods wrap context then delegate. Fallback store first queries main; on containerd not-found it queries fallback. `Walk` records digests seen in main, then walks fallback and suppresses duplicates.

State and persistence: no state beyond namespace strings and underlying content store. Persistence is delegated to containerd. Delete is intentionally blocked.

Dependencies and integration points: used when BuildKit shares containerd content across namespaces. Integrates with containerd content API and errdefs.

Risks and test signals: fallback is read-only for missing content; writes always go to main. `Delete` prohibition protects BuildKit from deleting shared content but may surprise generic content-store callers. No direct tests in this subset.
