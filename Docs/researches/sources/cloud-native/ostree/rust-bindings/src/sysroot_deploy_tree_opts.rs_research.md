# sources/cloud-native/ostree/rust-bindings/src/sysroot_deploy_tree_opts.rs

## sources/cloud-native/ostree/rust-bindings/src/sysroot_deploy_tree_opts.rs

Handwritten options struct for `ostree_sysroot_deploy_tree_with_options` and staging equivalents. `SysrootDeployTreeOpts<'a>` contains `locked`, optional `override_kernel_argv`, and optional `overlay_initrds`.

Control flow in `ToGlibPtr` zeroes an `OstreeSysrootDeployTreeOpts`, converts optional string slices into null-terminated C arrays, stores the backing conversions in the stash, and returns a stable pointer. State is per-deploy configuration only; persistence happens when sysroot deploy/stage methods write deployments.

Dependencies are `ffi::OstreeSysrootDeployTreeOpts`, GLib translation traits, and C string pointers. Risks include keeping nested array storage alive, zeroed C struct compatibility, and lifetime correctness for borrowed string slices. Tests validate default zero/null conversion and non-default string-array/locked conversion.
