# sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/cli.rs

Purpose: host-safe CLI integration suite for `cfsctl --insecure` and no-repo commands. It avoids root, fs-verity, and network requirements while checking core repository, OCI, fsck/gc, and mkcomposefs behavior.

Important APIs/types/functions: helper `init_insecure_repo` initializes V2 legacy EROFS repositories for pinned digest stability; `create_oci_layout` builds a deterministic minimal OCI layout with one layer and a hardlink; `corrupt_one_object` mutates repository object data for fsck tests. Constants include `OCI_LAYOUT_COMPOSEFS_ID`, composefs/EROFS magic bytes, and superblock offset.

Control flow: each function creates tempdirs, resolves `cfsctl`, runs commands through `xshell::cmd`, and asserts stdout/stderr/JSON/filesystem effects. Covered flows include GC empty/after-create/dry-run, image creation/idempotence/object listing, repository init metadata/algorithm/idempotence/conflicts/reset, hash auto-detection and mismatch failures, fsck healthy/corrupt/broken refs, OCI images/pull/inspect/layer/compute-id/tag/untag/gc, no-repo compute/dump behavior, and `mkcomposefs` byte-level output.

State and persistence: tests create temp repositories, rootfs fixtures, OCI layout directories, EROFS images, and intentionally corrupted object/ref states. They rely on tempdir cleanup. Repository metadata tests inspect `meta.json`, `objects`, `streams`, and `images`.

Dependencies and integration points: exercises public CLI behavior, not library internals, with JSON parsed by `serde_json`, tar output parsed by `tar`, dumpfile output parsed by `composefs_oci::composefs::dumpfile_parse`, and optional comparison to the C `mkcomposefs` binary if present.

Risks: pinned image IDs make EROFS writer changes visible but also require intentional updates when formats change. Many assertions inspect human-oriented output substrings, so output wording changes can break tests. The minimal OCI layout tests a controlled case, not registry/network pulls. The C mkcomposefs comparison is skipped when unavailable, so CI coverage depends on environment.

Test signals: this is the broadest fast regression suite for CLI semantics. Strong signals include deterministic image IDs, JSON schema expectations, nonzero fsck exit behavior, old-format migration hint presence, reset metadata preserving objects while removing streams/images, and mkcomposefs magic/determinism/hardlink behavior.
