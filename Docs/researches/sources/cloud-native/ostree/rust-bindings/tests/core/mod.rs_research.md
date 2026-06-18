# sources/cloud-native/ostree/rust-bindings/tests/core/mod.rs

Purpose: This Rust integration test verifies higher-level variant decoding for OSTree commit objects.

Important APIs, types, and functions: `variant_types` uses `TestRepo::new`, `test_commit`, `Repo::load_variant`, `ostree::ObjectType::Commit`, and `ostree::CommitVariantType`. It extracts the commit tuple and asserts that the subject field equals `Test Commit`.

Control flow: Create a temporary repository, write a test commit through shared utilities, load the commit object as a `GVariant`, decode it into the typed commit representation, and assert a known field.

State and persistence behavior: Creates a temporary archive-mode OSTree repo and writes one commit. State lives under `tempfile::TempDir` and is removed after the test.

Dependencies and integration points: Depends on `tests/util/mod.rs`, the safe `ostree` crate, GLib variant conversion, and the test data archive used by `create_mtree`.

Risks: It covers only one field of one commit variant. It assumes the utility commit subject remains `Test Commit`, so utility changes can break the test without a core variant regression.

Test signals: Passing confirms that commit `GVariant` loading and typed extraction work for at least the generated fixture commit.
