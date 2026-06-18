# sources/cloud-native/ostree/rust-bindings/src/tests/kernel_args.rs

## sources/cloud-native/ostree/rust-bindings/src/tests/kernel_args.rs

Unit tests for `KernelArgs`. They cover creating and filling argument sets, converting to string vectors, retrieving last key values, parsing from strings, appending arrays, filtered append, and replacing arrays.

Control flow is entirely in-memory against the boxed libostree kernel-args type. There is no persistence; the tests validate the values that would later be passed into sysroot deployment APIs. Dependencies are the crate `KernelArgs` wrapper and libostree's parsing/replacement behavior.

These tests are important because `KernelArgs` is a handwritten mutable boxed wrapper with unimplemented copy semantics. They verify practical command-line manipulation and guard against regressions in feature-gated kernel-argument support.
