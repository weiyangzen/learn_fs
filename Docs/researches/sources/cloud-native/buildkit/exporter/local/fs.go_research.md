# sources/cloud-native/buildkit/exporter/local/fs.go

Purpose: constructs the exported filesystem view shared by local and tar exporters. It mounts cache refs, applies idmap and epoch metadata normalization, filters attestations to inline-only data, unbundles attestations, creates in-toto statements over exported subjects, and merges statement files into the output filesystem.

Important APIs and types: `CreateFSOpts` holds `Epoch`, `AttestationPrefix`, and `PlatformSplit`; `UsePlatformSplit` defaults split behavior to multi-ref exports; `Load` parses exporter attrs including `source-date-epoch`, `platform-split`, `attestation-prefix`, and `mode`; `CreateFS` returns an `fsutil.FS`, cleanup function, and error.

Control flow: `CreateFS` either creates a temporary empty directory for nil refs or mounts an immutable ref with a session group. It wraps the root in `fsutil.NewFilterFS`, optionally remapping host ids into container ids and overriding `ModTime`. Attestations are filtered/unbundled, regular files are hashed as in-toto subjects, statements are marshaled to deterministic JSON, and a `staticfs` overlay is merged into the output.

State and persistence: temporary directories and mounted refs require caller cleanup. Attestation output exists only in the exported FS unless the caller transfers it. Duplicate statement filenames are rejected per export.

Dependencies and integration: used by local and tar exporters; integrates cache mounting, snapshot `LocalMounter`, session groups, `attestation.MakeInTotoStatements`, `result` metadata, `fsutil`, `staticfs`, and OCI digest helpers.

Risks and test signals: risks include cleanup leaks, idmap exclusion of unmappable files, duplicate attestation basenames, platform filename ambiguity when split is disabled, and expensive whole-tree hashing. Indirect coverage comes from local/tar export and attestation integration tests.
