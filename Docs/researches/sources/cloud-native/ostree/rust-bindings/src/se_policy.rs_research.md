# sources/cloud-native/ostree/rust-bindings/src/se_policy.rs

## sources/cloud-native/ostree/rust-bindings/src/se_policy.rs

Handwritten extension for `SePolicy`. It exposes `fscreatecon_cleanup`, a safe-looking wrapper around `ostree_sepolicy_fscreatecon_cleanup(NULL)` to reset SELinux filesystem creation context.

Control flow is a single unsafe FFI call with a null cleanup location. State affected is process/global SELinux creation context rather than Rust-owned data. This integrates with generated `SePolicy::setfscreatecon` and commit/checkout code that may set file labels.

Risk is global side effect: callers need to use it after setting fscreatecon so subsequent file creation is not mislabeled. There are no local tests, likely because behavior depends on SELinux runtime state.
