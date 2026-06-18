# sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_avahi.rs

## sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_avahi.rs

Generated object wrapper for `OstreeRepoFinderAvahi`, a concrete `RepoFinder` implementation for network discovery via Avahi. It exposes `RepoFinderAvahi::new` and implements the `RepoFinder` interface.

Control flow is constructor-only: Rust calls `ostree_repo_finder_avahi_new` and wraps the full pointer. Runtime discovery state, network interaction, and result production are delegated to libostree and Avahi. This file does not persist state itself; it creates an object intended to be passed into repo-finder orchestration elsewhere.

Dependencies are `ffi`, GLib translation traits, and `RepoFinder`. Risks are environmental rather than local: Avahi availability, network visibility, and feature support determine usefulness. There are no local tests.
