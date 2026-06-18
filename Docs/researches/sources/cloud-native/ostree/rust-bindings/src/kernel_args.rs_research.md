# sources/cloud-native/ostree/rust-bindings/src/kernel_args.rs

## sources/cloud-native/ostree/rust-bindings/src/kernel_args.rs

Handwritten boxed binding for `OstreeKernelArgs`, gated on newer libostree features. It supports creating/parsing kernel argument sets, appending individual or array args, filtering by prefixes, appending `/proc/cmdline`, deleting args or key entries, replacing args, querying the last value for a key, converting to string or string vector, and `Default`, `Display`, and `From<T: AsRef<str>>`.

Control flow delegates mutation to libostree's boxed type. The wrapper marks copy as unimplemented and uses libostree free, so callers should treat it as an owned mutable boxed object rather than a trivially cloneable Rust collection. State is in the boxed kernel-argument object and later feeds sysroot deploy/stage APIs; persistence happens only when deployments are written.

Dependencies are GLib boxed translation, `gio::Cancellable`, `GString`, and `ffi`. Risks include feature gating, unimplemented copy behavior, command-line parsing semantics delegated to libostree, and mutation through shared boxed references. Dedicated tests cover creation/fill, string-vector conversion, last-value lookup, parsing from string, append/filter/replace array behavior.
