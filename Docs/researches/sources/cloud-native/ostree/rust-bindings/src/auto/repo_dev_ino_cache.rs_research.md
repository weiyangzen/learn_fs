# sources/cloud-native/ostree/rust-bindings/src/auto/repo_dev_ino_cache.rs

## sources/cloud-native/ostree/rust-bindings/src/auto/repo_dev_ino_cache.rs

Tiny generated shared-wrapper binding for `OstreeRepoDevInoCache`. It exposes `RepoDevInoCache::new` and implements `Default`, delegating allocation and lifetime to `ostree_repo_devino_cache_new`, `ref`, and `unref`.

The cache is an integration helper for commit modifiers and checkout options, mapping device/inode pairs to checksums so libostree can detect already-known file content. There is no local control flow beyond creation and GLib pointer conversion. All state lives in the C shared object and is consumed by APIs such as `RepoCommitModifier::set_devino_cache` or `RepoCheckoutAtOptions`.

The main dependency is `ffi`; no filesystem persistence happens in this file directly. Risk is low but version-sensitive because consumers are feature-gated in other modules. There are no local tests; behavior is verified only when higher-level commit/checkout paths use the cache.
