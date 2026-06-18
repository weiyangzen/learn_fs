# sources/cloud-native/ostree/rust-bindings/src/auto/repo_commit_modifier.rs

## sources/cloud-native/ostree/rust-bindings/src/auto/repo_commit_modifier.rs

Generated shared-wrapper binding for `OstreeRepoCommitModifier`, used when writing directory trees or archives into a repo. The primary constructor `RepoCommitModifier::new` accepts `RepoCommitModifierFlags` and an optional Rust closure that maps `(Repo, path, FileInfo)` to `RepoCommitFilterResult`.

The file also exposes `set_devino_cache`, `set_sepolicy`, `set_sepolicy_from_commit`, and `set_xattr_callback`. These APIs connect commit creation to hardlink/device-inode caching, SELinux relabeling, and xattr synthesis. Control flow boxes Rust callbacks, passes them as `user_data`, and installs destroy notifiers so libostree can release the closures. State is held in the underlying shared C object; the Rust value is ref-counted via generated `ref`/`unref` hooks.

Dependencies are `Repo`, `RepoDevInoCache`, `SePolicy`, `gio::FileInfo`, and GLib translation traits. Risks center on callback lifetime and FFI unwinding: the generated commit-filter trampoline does not catch panics, so panics crossing into C would be unsafe. Feature gates limit newer cache and SELinux-from-commit helpers. Test coverage is indirect through commit/write paths; no local tests exist.
