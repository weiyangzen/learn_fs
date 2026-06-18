# sources/cloud-native/soci-snapshotter/integration/util_soci_test.go

Purpose: integration-test helpers for building and validating SOCI indexes through the real `soci` CLI, `nerdctl`, and local content stores. It centralizes index creation options, SOCI index descriptor validation, local-store digesting, and prefetch artifact validation.

Important APIs/types/functions: `indexBuildConfig` models `soci create` flags such as span size, min layer size, content store type, namespace, rebuild-db, force, and prefetch files. Functional options include `withSpanSize`, `withMinLayerSize`, `withContentStoreType`, `withNamespace`, `withForceRecreateZtocs`, and `withPrefetchPaths`. `buildIndex` pulls the source image with nerdctl, optionally rebuilds the SOCI DB, runs `soci create`, and returns the digest from `soci index list`. `validateSociIndex` checks media type, artifact type, annotations, subject digest, blob count, layer inclusion, blob size, and digest. `getSociLocalStoreContentDigest`, `sociIndexFromDigest`, and `assertPrefetchArtifactCreated` support store-state and artifact inspection.

Control flow: callers prepare an `imageInfo`, layer selection options, and a shell. `buildIndex` canonicalizes options, performs the pull, runs SOCI create, and queries index state. Validation then reads descriptors from content-store paths and compares actual bytes against OCI digest metadata. Prefetch validation follows descriptor annotations back to the image manifest and fetches the prefetch blob for decoding.

State and persistence: the file mutates integration container state: containerd content store, SOCI content store, SOCI DB, and optional prefetch artifacts. Digest helpers intentionally hash files larger than ten bytes in the SOCI blob path, so small metadata files do not affect the content-state fingerprint.

Dependencies/integration points: uses `util/dockershell`, `nerdctl`, `soci`, `soci/store`, `config.DefaultContentStoreType`, containerd namespaces/platforms, OCI descriptors, opencontainers digest, and `cmp.Diff`. It expects the integration container to have binaries and content-store paths available.

Risks: the helpers depend on exact CLI output shape, default annotation strings, and local content-store layouts. `buildIndex` returns an empty digest on list failure rather than an error, so calling tests must check for empty string. Prefetch validation assumes one prefetch descriptor for a requested path and that layer annotations are present.

Test signals: this file is itself test support; downstream integration tests exercise these helpers by creating indexes, validating descriptors, comparing content-store blob hashes, and asserting prefetch artifacts decode to non-empty span lists.
