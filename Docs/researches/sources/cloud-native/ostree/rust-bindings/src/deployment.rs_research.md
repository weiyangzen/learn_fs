# sources/cloud-native/ostree/rust-bindings/src/deployment.rs

## sources/cloud-native/ostree/rust-bindings/src/deployment.rs

Tiny handwritten extension for generated `Deployment`. It adds `stateroot`, currently an alias for `osname`, to expose OSTree deployment stateroot naming in Rust terms.

There is no control flow beyond forwarding, no persistence, and no independent state. Integration is with sysroot deployment APIs that return or accept `Deployment` objects.

Risk is semantic drift: if libostree's deployment terminology diverges from `osname`, this alias would need revisiting. No local tests are present.
