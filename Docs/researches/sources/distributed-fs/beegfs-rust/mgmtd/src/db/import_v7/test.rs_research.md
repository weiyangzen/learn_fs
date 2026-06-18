<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/import_v7/test.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/import_v7/test.rs

Purpose: end-to-end regression test for the v7 management data importer using a bundled v7.4 data archive.

Important APIs/types/functions: `import_v7()` test extracts `test_data.tar.gz` to a temporary directory, wraps execution in `catch_unwind()` for cleanup, then calls `import_v7_inner()`. The inner helper creates an in-memory DB, migrates schema, seeds initial entries, runs `super::import_v7()`, and checks imported rows.

Control flow: the test is skipped on Windows. It shells out to `tar`, imports from the extracted directory, then queries nodes, targets, buddy groups, root inode, storage pools, quota defaults, and quota limits in deterministic order.

State and persistence: uses only an in-memory SQLite database plus a temporary extracted fixture directory. It does not write production state.

Dependencies and integration points: verifies `db::MIGRATIONS`, `initial_entries()`, SQLite enum conversions, importer parsing, and schema compatibility together.

Risks: depends on the external `tar` command and fixture archive path. It validates one representative v7 layout, not all malformed files, missing files, alias-prompt paths, or non-GOOD target states.

Test signals: strong integration signal that the importer creates expected rows for a real v7.4-style dataset, including quota data and mirrored meta root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/import_v7/test.rs -->
