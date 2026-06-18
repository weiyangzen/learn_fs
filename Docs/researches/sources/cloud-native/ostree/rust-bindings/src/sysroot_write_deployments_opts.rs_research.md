# sources/cloud-native/ostree/rust-bindings/src/sysroot_write_deployments_opts.rs

## sources/cloud-native/ostree/rust-bindings/src/sysroot_write_deployments_opts.rs

Handwritten options struct for `ostree_sysroot_write_deployments_with_options`. `SysrootWriteDeploymentsOpts` currently exposes `do_postclean`.

Control flow zeroes an `OstreeSysrootWriteDeploymentsOpts`, sets the GLib boolean, boxes it for pointer stability, and returns a `ToGlibPtr` stash. State is per-call configuration; persistent effects are in the generated sysroot deployment-writing method.

Dependencies are `ffi::OstreeSysrootWriteDeploymentsOpts` and GLib translation traits. Risks are low but include C layout/version compatibility and interpreting cleanup side effects. Tests verify default `GFALSE` and non-default `GTRUE` conversion.
