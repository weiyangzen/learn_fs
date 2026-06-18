# sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_override.rs

## sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_override.rs

Generated object wrapper for `OstreeRepoFinderOverride`, a concrete `RepoFinder` intended to use caller-specified overrides. It provides `new`, `Default`, and property accessors for `substitutions`.

The control flow is basic GObject construction and property get/set through `ObjectExt`. State is held on the GObject property and then consumed by libostree finder logic. This file does not write disk state; it configures runtime discovery behavior.

Dependencies are `RepoFinder`, GLib object property APIs, and `ffi`. Risks include variant/property shape correctness and callers assuming substitutions are validated locally; validation is deferred to libostree. There are no local tests.
