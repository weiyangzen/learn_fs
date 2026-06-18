# sources/cloud-native/containerd/plugins/diff/erofs/compare_linux.go

## Purpose
Implements Linux-only EROFS differ comparison by generating a standard OCI layer tar diff from EROFS snapshot mounts and storing it in the content store.

## Important APIs, Types, And Functions
`writeDiff` mounts the lower mount set and streams overlay-style directory changes from the upper root. `erofsDiff.Compare` handles diff options, media-type compression selection, content writer lifecycle, uncompressed digest labels, commits, and descriptor construction. `uniqueRef` creates upload references.

## Control Flow
Compare converts the upper mount to an EROFS layer path, applies diff options and source-date epoch, defaults media type to gzip, opens or truncates a content writer, writes a tar diff from `layer/fs`, optionally compresses while hashing the uncompressed stream, commits by writer digest, fetches content info, patches missing uncompressed labels, and returns an OCI descriptor.

## State And Persistence
Persists diff blobs and labels in the content store. Temporary state is the content ingest reference and mounted lower filesystem. Failed new-reference writes abort the ingest.

## Dependencies And Integration Points
Uses `continuity/fs`, `archive.NewChangeWriter`, compression helpers, `epoch`, content store APIs, EROFS mount-to-layer utilities, and OCI media types. It is selected by the EROFS diff plugin on Linux.

## Risks
The path assumption `layer/fs` must match EROFS snapshot layout. Label repair assumes `config.Labels` has an uncompressed digest, which is only guaranteed for compressed writes. Writer cleanup and existing-content label update are important for interrupted or deduplicated diffs.

## Test Signals
No direct tests in this subset. Behavior is exercised by containerd diff/apply integration tests and EROFS snapshot/differ workflows.
