# sources/cloud-native/soci-snapshotter/integration/pull_test.go

Purpose: broad end-to-end coverage for lazy pulling, sparse indexes, deterministic artifact generation, malformed artifacts, mirrors, unmount cleanup, min-layer-size runtime filtering, full-layer reads, parallel pull, and custom decompression.

Important APIs and flow: `TestOptimizeConsistentSociArtifact` rebuilds artifacts and byte-compares content-store blobs. `TestLazyPullWithSparseIndex` compares tar output with normal snapshotter output and verifies small layers are local while indexed layers are FUSE mounts. `TestLazyPull` covers optimized, non-optimized, and multi-image pulls with and without background fetch. `TestLazyPullNoIndexDigest` uses referrers discovery. `TestPullWrongIndexDigest` confirms a valid index for a different image is recorded but all real layers mount locally. `TestPullWithAribtraryBlobInvalidZtocFormat` injects random zTOC bytes and expects local fallback with matching contents. `TestMirror` exercises registry mirror failover and refresh using iptables. Later tests cover removing images unmounting FUSE, runtime min-layer-size, full-layer fetched-percent JSON, parallel fetch/unpack, and rapidgzip/igzip/pigz decompression streams.

State and persistence: mutates registries, content stores, iptables rules, FUSE mounts, image tags, and container runtime state.

Dependencies and integration: uses SOCI CLI, containerd/nerdctl, registries with cert/auth, OCI JSON, zTOC/index injection, metrics, iptables, and tar/diff content comparison helpers.

Risks and test signals: highest-value behavioral coverage for lazy pulling. Risks are environmental flakiness: network, image availability, registry DNS/certs, iptables cleanup, FUSE mount cleanup, and timing around background fetch or metrics.
