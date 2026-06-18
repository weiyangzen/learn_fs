# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/testdata/output.json

Purpose: test fixture modeling `nydus-image` build output consumed by packer.

Important fields: `version`, `blobs`, and nested `trace` metrics. The `blobs` array contains the digest-like blob hash used by tests.

Control flow and state: `getNewBlobsHash` reads this file and returns the first blob hash not present in parent/chunk-dict lists. Pack and pusher tests copy it to temporary output dirs to drive blob rename/push behavior.

Dependencies and integration points: packer `BlobManifest` only consumes `blobs`; trace content is ignored by current code but represents realistic builder output.

Risks and test signals: fixture confirms parser tolerates extra fields. It has a single blob, so multi-blob ordering behavior is covered only by separate generated JSON in tests.
