# sources/cloud-native/stargz-snapshotter/fs/source/source.go

## Purpose
Converts containerd snapshot/image labels into typed remote blob source information and appends the labels needed by stargz snapshotter during unpack.

## Important APIs, Types, And Functions
`GetSources` and `RegistryHosts` are function types. `Source` carries registry hosts, image reference, target descriptor, and manifest layer context. `FromDefaultLabels` parses stargz labels into `Source`. `AppendDefaultLabelsHandlerWrapper` annotates layer descriptors during image traversal. `AppendExtraLabelsHandler`, `appendWithValidation`, and `layerFromDigest` add optional URL and prefetch metadata while respecting label size limits.

## Control Flow
Default label parsing requires reference and digest labels, optionally parses neighboring layer digests and per-index URLs, copies target URLs into descriptor URLs, and returns one source. Handler wrappers intercept manifest children, identify layer descriptors, populate annotations with reference, digest, later layer digests, neighboring URLs, prefetch size, and layer URLs.

## State And Persistence
No long-lived local state. State is embedded in OCI descriptor annotations and later persisted by containerd snapshot labels. Label validation can truncate optional lists, affecting prefetch optimization rather than correctness.

## Dependencies And Integration
Depends on containerd images, labels, Docker registry references, snapshotter config labels, OCI descriptors, and opencontainers digest parsing. It is the handoff between image unpack/conversion and remote filesystem resolution.

## Risks And Test Signals
Risks include missing required labels, invalid digest strings, label length truncation, and mismatched layer-index URL annotations. Tests are not in this subset; integration signal is downstream snapshot mount resolving sources successfully and pre-resolving neighboring layers when labels are present.
