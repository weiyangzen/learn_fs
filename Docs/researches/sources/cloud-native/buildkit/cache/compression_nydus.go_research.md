# sources/cloud-native/buildkit/cache/compression_nydus.go

Purpose: optional `nydus` build-tag support for merging per-layer Nydus bootstraps into an additional gzip-compressed bootstrap layer descriptor.

Important APIs/types/functions: `init` appends Nydus blob/bootstrap annotations to `additionalAnnotations`. `MergeNydus` accepts an `ImmutableRef`, compression config, and session group, returning an OCI descriptor for the merged bootstrap tar layer.

Control flow: `MergeNydus` type-checks the ref as `*immutableRef`, obtains the layer chain, resolves a Nydus-compressed blob for each layer via `getBlobWithCompressionWithRetry`, opens each blob as `ReaderAt`, pipes converter merge output into a gzip writer backed by a content-store writer, records the uncompressed digest, commits the compressed content, and returns a descriptor annotated as a Nydus bootstrap layer.

State and persistence behavior: writes a new content blob to the content store with `containerd.io/uncompressed` label. It does not attach the descriptor to a ref by itself; callers use the returned descriptor during export/manifest construction.

Dependencies and integration points: integrates containerd content, labels, BuildKit compression/session APIs, OCI descriptors, and `containerd/nydus-snapshotter/pkg/converter`. The file is excluded unless built with `nydus`.

Risks: all layer readers are deferred until function exit, so very deep layer chains keep descriptors open. Pipe/goroutine error propagation depends on `CloseWithError`. Missing Nydus compression variants fail the merge.

Test signals: no direct tests in this subset; requires nydus-tag integration tests to validate converter behavior and descriptor annotations.
