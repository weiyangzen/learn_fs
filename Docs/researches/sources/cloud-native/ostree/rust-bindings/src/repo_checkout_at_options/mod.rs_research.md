# sources/cloud-native/ostree/rust-bindings/src/repo_checkout_at_options/mod.rs

## sources/cloud-native/ostree/rust-bindings/src/repo_checkout_at_options/mod.rs

Handwritten Rust representation for `OstreeRepoCheckoutAtOptions`. The struct exposes checkout mode, overwrite mode, fsync and whiteout controls, hardlink/copy behavior, optional subpath, devino cache, SELinux policy, and a feature-gated checkout filter.

Control flow is in `Default` and `ToGlibPtr`: it builds a zeroed C `OstreeRepoCheckoutAtOptions` in boxed storage, converts optional path/string/callback fields, assigns flags, and returns a stable pointer stash for the duration of the FFI call. State is per-call checkout configuration; filesystem persistence happens in `Repo::checkout_at`.

Dependencies include `RepoCheckoutMode`, `RepoCheckoutOverwriteMode`, `RepoDevInoCache`, `SePolicy`, `RepoCheckoutFilter`, `libc::c_char`, and GLib conversion traits. Risks include keeping all nested storage alive, C struct layout/version compatibility, and feature-gated fields matching the linked libostree. Tests validate default and non-default C conversion, including pointer/string fields.
