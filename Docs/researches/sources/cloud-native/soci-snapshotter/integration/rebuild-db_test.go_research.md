# sources/cloud-native/soci-snapshotter/integration/rebuild-db_test.go

Purpose: validates `soci rebuild-db` reconstructs artifact database entries from content-store blobs and drops entries when blobs are removed.

Important APIs and flow: `TestRebuildArtifactsDB` builds and decodes an index for RabbitMQ, pushes artifacts, and defines `verifyArtifacts` to count `soci index list` and `soci ztoc list` output rows. Test cases cover remote pull followed by rebuild, expecting one index and all zTOCs, and deliberate removal of index/zTOC blobs followed by rebuild, expecting zero entries. Each case is run for every content-store type.

State and persistence: mutates selected content stores by pulling artifacts or deleting content blobs, then runs database rebuild.

Dependencies and integration: uses SOCI CLI, registry helpers, content-store path helpers, direct content removal helpers, and SOCI index decoding.

Risks and test signals: direct signal for artifact DB repair after content-store drift. Counting rows from human-readable CLI output is format-sensitive. The misspelled `exptectedZtocCount` field is harmless but reduces readability.
