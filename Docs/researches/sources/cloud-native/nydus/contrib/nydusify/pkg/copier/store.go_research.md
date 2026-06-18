# sources/cloud-native/nydus/contrib/nydusify/pkg/copier/store.go

Purpose: wraps a containerd `content.Store` so newly added remote backend blob descriptors can be reported as present even when they are not in the local content store.

Important APIs/types/functions: unexported `store`, `newStore`, and `Info`.

Control flow: `Info` delegates to the embedded base store. If the base store returns an error other than not found, the error is preserved. If the digest is not found, the wrapper searches its `remotes` descriptor slice and returns synthetic `content.Info` with digest and size for a matching remote descriptor; otherwise it returns the original not-found error.

State and persistence: the wrapper stores only an in-memory descriptor slice and delegates all other content-store methods through embedding. It does not persist or fetch actual content.

Dependencies and integration points: containerd content store and errdefs, OCI descriptors, and copier manifest push flow after `pushBlobFromBackend` prepends backend blobs.

Risks and test signals: synthetic info can make remote-only blobs visible to code that checks content existence, but read paths still depend on the underlying store/provider. Duplicate descriptors return the first match.
