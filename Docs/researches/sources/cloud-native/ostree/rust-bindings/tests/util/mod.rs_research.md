# sources/cloud-native/ostree/rust-bindings/tests/util/mod.rs

Purpose: This shared test utility module creates temporary OSTree repositories, writes fixture commits, and verifies checkout content for the Rust binding integration tests.

Important APIs, types, and functions: `TestRepo` stores a `tempfile::TempDir` and `ostree::Repo`. `TestRepo::new` and `new_with_mode` create archive-mode repos by default. `test_commit` writes a fixture commit. Feature-gated `CapTestRepo` uses `cap_tempfile` and `Repo::create_at_dir`. `create_mtree` creates a `MutableTree`, asserts initially empty copied files/subdirs, and imports `rust-bindings/tests/data/test.tar` through `write_archive_to_mtree`. `commit` uses `auto_transaction`, `write_mtree`, `write_commit`, `transaction_set_ref`, and transaction commit. `assert_test_file` reads `test-checkout/testdir/testfile` and expects `test\n`.

Control flow: Repo helpers create temp storage, initialize libostree repos, import a tar fixture into a mutable tree, write it to the repo, create a commit with subject `Test Commit`, set a ref, and commit the transaction. Tests call these helpers to avoid duplicating setup.

State and persistence behavior: All state is temporary but realistic: repo config, object storage, refs, transaction state, mutable trees, and checkout directories. Transaction helper is the key persistence boundary for commits and refs.

Dependencies and integration points: Depends on GLib prelude traits, GIO file APIs, `tempfile`, optional `cap_tempfile`, the `ostree` safe crate, and the fixture archive path resolved via `CARGO_MANIFEST_DIR`.

Risks: Many tests depend on exact fixture contents and commit subject. Any change to `test.tar` can update object checksums, object counts, and checkout assertions. The helper panics on setup failures, which is appropriate for tests but not reusable production logic.

Test signals: Because most integration tests use this module, successful test setup across modules is a broad signal that repo initialization, archive import, transaction commit, and fixture checkout remain healthy.
