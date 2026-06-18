# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/stream_content.go

Purpose: implements `StreamContent`, a `content.Store` adapter that avoids ingesting pulled remote content locally while still supporting generated JSON/blob writes needed by converter handlers.

Important APIs/types/functions: `StreamContent`, `NewStreamContent`, `SetDefaultRef`, `Writer`, `ReaderAt`, `Info`, `Update`, `Walk`, `Delete`, ingest status methods, `memWriter`, `bytesReaderAt`, `copyMap`, `isFetchRef`, and `hasPrefix`.

Control flow: `Writer` classifies containerd fetch refs with prefixes such as `manifest-`, `index-`, `layer-`, `config-`, and `attestation-`; those return `ErrAlreadyExists` so fetch code treats content as already available remotely. Non-fetch refs receive a `memWriter`, whose `Commit` stores bytes keyed by expected or computed digest. `ReaderAt` first checks in-memory generated blobs, then fetches remotely with `remote.Fetch` using `defaultRef`.

State and persistence: labels, generated blobs, and `defaultRef` are in-memory behind an RW mutex. No durable local content is stored; `Walk` is empty and `Delete` only clears in-memory maps.

Dependencies and integration points: containerd content store interfaces, `errdefs`, Harbor acceleration-service registry fetch helpers, OCI descriptors, and digest validation.

Risks and test signals: default-ref absence is a hard not-found path. `memWriter.Truncate` does not reset the incremental digester, so digest after truncation can reflect pre-truncation data unless commit uses an expected digest. Tests document this behavior.
