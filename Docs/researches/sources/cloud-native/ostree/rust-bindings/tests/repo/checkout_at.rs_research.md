# sources/cloud-native/ostree/rust-bindings/tests/repo/checkout_at.rs

Purpose: This test module verifies the safe Rust `Repo::checkout_at` wrapper, including `None` options, default options, explicit checkout options, and optional checkout filtering.

Important APIs, types, and functions: Tests use `TestRepo`, `cap_std::fs::Dir`, `AsRawFd`, `RepoCheckoutAtOptions`, `RepoCheckoutMode::User`, `RepoCheckoutOverwriteMode::AddFiles`, `RepoDevInoCache::new`, `RepoCheckoutFilter::new`, and filter results `Allow`/`Skip`. `assert_test_file` verifies checked-out content.

Control flow: Each test creates a temporary repo and commit, opens a capability directory for a temp checkout root, calls `checkout_at` with a destination fd and path, then verifies filesystem output. The filter test conditionally skips `/testdir/testfile` and asserts the directory exists but the file does not.

State and persistence behavior: Writes a temporary checkout tree on disk. The third test also creates a devino-to-checksum cache for checkout acceleration/canonicalization behavior. The filter closure is transient callback state passed through FFI.

Dependencies and integration points: Depends on libostree checkout-at API, capability-oriented directory handles from `cap-std`, Unix raw file descriptors, and feature gates for APIs introduced around `v2016_8` and `v2018_2`.

Risks: File descriptor lifetime and callback ownership are important unsafe boundaries. The filter path comparison assumes libostree reports paths with a leading slash. The tests validate success cases but not overwrite conflict handling or SELinux policy options.

Test signals: Passing confirms `checkout_at` accepts null/default/non-default option structs, can use a devino cache, and can invoke Rust filter callbacks safely enough to affect checkout output.
