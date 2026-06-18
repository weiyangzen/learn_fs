# sources/cloud-native/ostree/tests/test-commit-sign-sh-ext.c

Purpose: C companion test for commit signature verification APIs, invoked by the shell GPG signing test when running uninstalled.

Important APIs/functions: `ostree_repo_resolve_rev`, `ostree_repo_load_variant`, `ostree_repo_read_commit_detached_metadata`, `ostree_repo_signature_verify_commit_data`, helper `corrupt()`, and `assert_error_contains()`.

Control flow: opens the test repo, loads `origin:main` commit data and detached metadata, verifies signatures for remote `origin`, then checks expected failures for no enabled verification types, empty metadata, missing remote, and corrupted commit bytes.

State/persistence: reads an existing repo prepared by `test-commit-sign.sh`; no writes beyond process allocations. Dependencies include signed test data, GLib, and libostree signature modules.

Integration/risk/test signals: protects lower-level signature verification independent of CLI pull. Risks are relying on caller-prepared repo/remotes and exact error substrings. Exit status from the C test is the signal.
