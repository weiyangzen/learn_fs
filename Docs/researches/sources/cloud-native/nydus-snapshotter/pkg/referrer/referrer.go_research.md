# Research: sources/cloud-native/nydus-snapshotter/pkg/referrer/referrer.go

This file implements the registry-facing OCI referrers detector. A `referrer` owns a `remote.Remote`. `checkReferrer` fetches the referrers index for a manifest digest through a `ReferrersFetcher`, limits reads to 8 MiB, unmarshals an OCI index, fetches the first returned manifest, validates it has layers, and returns the last layer when it is marked as a Nydus metadata layer. It retries once with plain HTTP when the remote deems that valid.

`fetchMetadata` skips work if the target metadata file already exists, fetches the selected descriptor, and calls `remote.Unpack` to extract the bootstrap file, removing partial metadata on unpack failure. State is remote registry content and the local metadata file path.

Dependencies include auth-backed remote resolvers, custom referrers fetcher interface, OCI image specs, converter bootstrap filename, Nydus labels, and filesystem operations. Risks include choosing only `index.Manifests[0]` despite a TODO about artifact type search, stale existing metadata files, partial-output cleanup, referrers API compatibility, and no tests in this subset.
