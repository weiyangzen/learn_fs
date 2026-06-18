# sources/cloud-native/ostree/rust-bindings/src/constants.rs

## sources/cloud-native/ostree/rust-bindings/src/constants.rs

Small handwritten constants module. It exports `COMMIT_META_CONTAINER_CMD`, the OSTree commit metadata key `"ostree.container-cmd"`.

There is no control flow or state. The constant integrates callers with commit metadata dictionaries used when storing container command metadata in OSTree commits. The only dependency is downstream code that imports it from `lib.rs`.

Risks are limited to string-key drift if libostree changes conventions; no tests are present because the file is a fixed constant.
