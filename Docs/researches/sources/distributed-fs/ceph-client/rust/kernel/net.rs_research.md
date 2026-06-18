# sources/distributed-fs/ceph-client/rust/kernel/net.rs

Purpose: top-level networking module gate for Rust kernel networking abstractions.

Important APIs/types/functions: conditionally exports `pub mod phy` when `CONFIG_RUST_PHYLIB_ABSTRACTIONS` is enabled.

Control flow: there is no runtime control flow. The file is purely a compile-time module declaration controlled by kernel configuration.

State and persistence behavior: none.

Dependencies and integration points: depends on `CONFIG_NET` at the parent `lib.rs` export level and `CONFIG_RUST_PHYLIB_ABSTRACTIONS` for PHY support. It is the namespace through which callers reach `kernel::net::phy`.

Risks: missing or incorrect cfg flags can hide PHY abstractions from users or build them when dependencies are unavailable. Because this file is small, most behavioral risk lives in `net/phy.rs`.

Test signals: build matrix coverage with networking on/off and PHY Rust abstractions on/off is sufficient.
