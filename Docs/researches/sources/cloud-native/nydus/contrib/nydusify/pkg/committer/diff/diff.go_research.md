# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/diff.go

Purpose: builds a tar diff stream from overlay snapshot lower/upper directories for container commit.

Important APIs and flow: `overlaySupportIndex` detects kernel overlay index support. `writeUpperdir` creates an empty lower dir, overlays upperdir over it, mounts the real lower snapshot, constructs `archive.ChangeWriter`, and calls `Changes` to emit change records. `Diff` appends an empty lower to the lowerdir list, creates lower and upper overlay mount definitions, finds the real upperdir with BuildKit overlay logic, then calls `writeUpperdir` with a cancellable writer.

State and persistence: creates temporary empty lower directories and temporary overlay mounts through containerd mount helpers; writes diff data to caller's writer.

Dependencies and integration: called by `Committer.commitUpperByDiff`. Depends on containerd mount, BuildKit overlay helpers, and local archive writer.

Risks and test signals: requires Linux overlay mount support and privileges. Incorrect lowerdir ordering or unsupported overlay options can produce wrong diffs or fail. It appends an empty lower to avoid overlay constraints.
