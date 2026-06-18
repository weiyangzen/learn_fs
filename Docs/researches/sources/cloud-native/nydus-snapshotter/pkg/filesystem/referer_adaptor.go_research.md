# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/referer_adaptor.go

This adaptor connects `Filesystem` to the OCI referrers-based metadata detector. `ReferrerDetectEnabled` checks whether a referrer manager is configured. `CheckReferrer` extracts the image reference and manifest digest from containerd labels, validates the digest, and delegates to `referrerMgr.CheckReferrer`. `TryFetchMetadata` validates the same labels and calls `referrerMgr.TryFetchMetadata` to fetch and unpack metadata to a path.

No local persistence is managed here except passing `metadataPath` to lower layers. The lower referrer manager maintains an LRU descriptor cache and writes metadata via `remote.Unpack`. This file is part of the metadata discovery decision path used when a Nydus metadata layer is published as an OCI referrer instead of directly in the pulled manifest.

Risks include returning false for all label or registry errors in `CheckReferrer`, dereferencing `fs.referrerMgr` in `TryFetchMetadata` without a local nil guard, and relying on label-provided manifest digest correctness. The code uses the package name `referer` in the filename but `referrer` in types and package paths. There are no direct tests for this adaptor in the subset.
