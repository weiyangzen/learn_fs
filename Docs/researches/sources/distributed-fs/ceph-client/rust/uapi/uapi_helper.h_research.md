# sources/distributed-fs/ceph-client/rust/uapi/uapi_helper.h

Purpose: central header input for bindgen when generating Rust UAPI bindings.

Important APIs/types/functions: includes UAPI headers for generic ioctl numbers, DRM core and device-specific DRM ioctls, Android binder, MDIO/MII, and ethtool.

Control flow: no runtime flow; preprocessor inclusion order determines what bindgen sees.

State and persistence: no state. Changes affect the generated `uapi_generated.rs` artifact consumed by the Rust `uapi` crate.

Dependencies and integration: consumed by the kernel Rust build's bindgen step and paired with `rust/uapi/lib.rs`. Header availability depends on a configured kernel source tree and installed/generated UAPI headers.

Risks: include ordering and newly added headers can introduce duplicate definitions, unsupported C constructs, or ABI drift. The file says headers are sorted alphabetically, but the current order groups DRM before Android/Linux networking, so maintainers should be deliberate when modifying it.

Test signals: successful bindgen generation, Rust crate compilation, and layout/constant checks for binder, DRM, ethtool, MDIO, MII, and ioctl bindings.
