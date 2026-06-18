# sources/cloud-native/soci-snapshotter/integration/push_test.go

Purpose: validates pushing and re-pulling SOCI artifacts, registry authentication, most-recent-index selection, OCI registry compatibility, and existing-index policies.

Important APIs and flow: `TestSociArtifactsPushAndPull` builds platform-specific indexes, pushes artifacts, deletes local blobs, remote-pulls with the index digest, and compares local artifact-store digests. `TestPushWithUserFlag` removes Docker auth config and checks `--user` and `-u` succeed while no flag fails. `TestPushAlwaysMostRecentlyCreatedIndex` builds multiple indexes with different options and expects `--existing-index allow -q` to push the latest digest. `TestLegacyOCI` verifies OCI 1.0 artifacts work against OCI 1.0 and 1.1 registries and are usable for lazy pulls. `TestPushWithExistingIndices` verifies warn, skip, allow, and multiple-existing-index behaviors via referrers counts and output messages.

State and persistence: creates/pushes registry artifacts, removes local SOCI blobs, modifies Docker auth config, and queries registry referrers.

Dependencies and integration: uses local registries, SOCI CLI, `nerdctl`, content-store digest helpers, platform parsing, OCI referrers, and SOCI index JSON.

Risks and test signals: strong registry interoperability and CLI policy coverage. Output-message assertions are brittle, and tests rely on registry implementations supporting the expected OCI artifact/referrers behavior.
