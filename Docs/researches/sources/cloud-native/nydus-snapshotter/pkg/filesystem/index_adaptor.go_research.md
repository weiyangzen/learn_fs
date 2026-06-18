# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/index_adaptor.go

This adaptor connects `Filesystem` to the OCI index-alternative detector. `IndexDetectEnabled` reports whether an `index.Manager` is configured. `CheckIndexAlternative` validates required snapshot labels, detects an explicit `containerd.io/snapshot/nydus-index-alternative=true` fast path, then calls `indexMgr.CheckIndexAlternative` with the image ref and target manifest digest. `TryFetchMetadataFromIndex` validates labels, skips work if the metadata file already exists, and delegates to `indexMgr.TryFetchMetadata`.

State is mostly external: labels describe the image, `metadataPath` is written by the index manager, and the manager caches descriptors by manifest digest. This adaptor decides whether filesystem preparation should use an alternative Nydus manifest from an OCI index rather than a referrer or normal layer.

Dependencies include containerd snapshotter labels, Nydus label constants, OpenContainers digests, filesystem existence checks, logging, and `pkg/index`. Risks include silently returning false for missing/invalid labels, trusting the explicit label without rechecking the registry, and not checking `indexMgr` nil in `TryFetchMetadataFromIndex`. Tests for descriptor selection live in `pkg/index`, not this adaptor.
