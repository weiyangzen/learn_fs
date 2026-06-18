# sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder.rs

## sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder.rs

Generated interface wrapper for `OstreeRepoFinder`. It provides the marker object/interface and an empty `RepoFinderExt` trait implemented for all `IsA<RepoFinder>` types. The imported `RepoFinderResult` signals the intended integration surface, while concrete behavior is supplied by specific finder implementations.

There is no local persistence or algorithmic control flow here. State and discovery mechanics live in implementations such as config, mount, override, or Avahi finders and in libostree itself. Dependencies are GLib object/interface glue and the crate-level `ffi` module.

The risk is mostly API-completeness: as generated, this file does not expose active finder methods, so users rely on concrete finder constructors and repo APIs. There are no local tests; behavior is covered only by consumers of concrete finder wrappers.
