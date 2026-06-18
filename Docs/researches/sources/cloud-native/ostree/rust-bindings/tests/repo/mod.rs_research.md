# sources/cloud-native/ostree/rust-bindings/tests/repo/mod.rs

Purpose: This is the main integration test module for safe `ostree::Repo` behavior: creating commits, resolving refs, listing commits, capability-based repo creation, traversing and reading objects, checkout, object copying, and repo file descriptor access.

Important APIs, types, and functions: It imports `ostree::prelude::*`, `ObjectName`, `ObjectType`, and conditionally `cap_std`. Tests cover `require_rev`, `create_mtree`, `commit`, `Repo::new_for_path`, `open`, `list_refs`, `list_commit_objects_starting_with`, `Repo::create_at_dir`, `Repo::open_at_dir`, `traverse_commit`, `read_dirmeta`, `query_file`, `read_commit`, `checkout_tree`, `load_object_stream`, `write_content`, `load_variant`, `write_metadata`, and `dfd_as_file`.

Control flow: The tests build temporary repositories from the shared tar fixture, perform operations through safe wrappers, and assert exact checksums/counts/content. Helper functions `copy_file` and `copy_metadata` copy traversed objects from one repo to another and assert output checksums match source object names.

State and persistence behavior: Temporary archive-mode repos are created and mutated with commits, refs, object files, metadata variants, and checkouts. Transactions in `util::commit` ensure ref updates are committed atomically. Capability tests use directory fds to avoid ambient path access for newer feature sets.

Dependencies and integration points: Integrates the safe Rust crate with raw FFI, GLib/GIO, cap-std feature-gated APIs, Unix metadata APIs, and fixed fixture checksums from `tests/data/test.tar`.

Risks: Exact object checksums and mode expectations are fixture- and environment-sensitive; comments note uid/gid are from the test runner, while mode is asserted. The module verifies representative flows but does not cover remote pull, pruning, locking, or error recovery.

Test signals: Passing provides broad confidence that core repo wrappers marshal strings, variants, streams, fds, transactions, object names, and checkout parameters correctly.
