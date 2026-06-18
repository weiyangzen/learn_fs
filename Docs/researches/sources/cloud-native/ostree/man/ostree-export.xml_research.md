# sources/cloud-native/ostree/man/ostree-export.xml

Purpose: documents `ostree export`, which exports a commit/tree as an archive stream.

Important APIs/types: synopsis targets a branch/commit and options for output behavior.

Control flow: resolves the target commit and serializes its tree to a tar-like stream suitable for external consumers.

State and persistence: read-only for repository objects; writes archive bytes to stdout or target stream depending on implementation/options.

Dependencies and integration: integrates repository object reading, archive/libarchive support from configure, and distribution/export workflows.

Risks and test signals: risks include metadata/xattr preservation, stream errors, and archive compatibility. Signals are export/import round trips and tar metadata tests.
