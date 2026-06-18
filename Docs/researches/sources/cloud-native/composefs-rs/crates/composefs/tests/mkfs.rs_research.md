# sources/cloud-native/composefs-rs/crates/composefs/tests/mkfs.rs

Purpose: integration-style Rust tests for EROFS image generation, byte stability, fsck compatibility, and equivalence with the C `mkcomposefs` tool.

Important APIs/types/functions: `default_stat`, `debug_fs`, `empty`, `add_leaf`, `simple`, `foreach_case`, `dump_image`, tests `test_empty`, `test_simple`, `test_fsck`, `test_vs_mkcomposefs`, `test_erofs_digest_stability`, `test_erofs_v1_digest_stability`, and `test_vs_mkcomposefs_min_version_1`.

Control flow: canonical in-memory trees are generated, rendered through `mkfs_erofs` or `mkfs_erofs_versioned`, optionally passed to `fsck.erofs`, compared byte-for-byte to C `mkcomposefs` output from dumpfile input, and checked against pinned fs-verity digests.

State/persistence: temporary image files are created for external tools. Pinned digest constants are persistent compatibility contracts, especially for bootc sealed UKI trust chains where image bytes must stay stable.

Dependencies/integration: integrates composefs dumpfile, EROFS writer/debug code, fs-verity hashing, `insta` snapshots, `similar_asserts`, `test_with` executable gates, `fsck.erofs`, and C `mkcomposefs`.

Risks/test signals: high-value tests catch layout drift and C compatibility regressions. Tests gated on external executables may silently skip in constrained environments, so CI needs those tools for full coverage. Intentional format changes require updating snapshots and pinned digests with care.
