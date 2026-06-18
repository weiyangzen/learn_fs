# sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_result.rs

## sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_result.rs

Generated boxed/shared wrapper for `OstreeRepoFinderResult`. It exposes comparison ordering by delegating `PartialEq`, `PartialOrd`, and `Ord` to `ostree_repo_finder_result_compare`.

The type represents finder output produced by libostree discovery mechanisms. This Rust file mainly manages ownership and ordering semantics; it has no constructors or direct persistence. State is the underlying C result object and any associated remote metadata carried by libostree.

Dependencies are `ffi` and GLib translation. Risks are around opaque semantics: Rust ordering reflects C comparison behavior, so consumers should not infer more than libostree guarantees. No local tests exist.
