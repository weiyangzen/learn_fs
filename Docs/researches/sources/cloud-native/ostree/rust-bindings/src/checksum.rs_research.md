# sources/cloud-native/ostree/rust-bindings/src/checksum.rs

## sources/cloud-native/ostree/rust-bindings/src/checksum.rs

Handwritten safe wrapper around a binary SHA-256 OSTree checksum. `Checksum` owns a `g_malloc`/`g_free`-compatible 32-byte buffer and offers `from_bytes`, `from_hex`, `from_base64`, `to_hex`, `to_base64`, `Display`, `Clone`, equality via `ostree_cmp_checksum_bytes`, and GLib pointer conversion implementations. `ChecksumError` distinguishes invalid hex and invalid OSTree-modified-base64 input.

Control flow allocates zeroed GLib memory, decodes or copies exactly `OSTREE_SHA256_DIGEST_LEN` bytes, and frees on `Drop`. The base64 engine uses OSTree's modified alphabet with `_` instead of `/` and no required padding. State is only the owned checksum bytes; persistence occurs when repo write functions return or consume checksums.

Dependencies are `base64`, `hex`, `once_cell`, GLib allocation APIs, and `ffi`. Risks include raw pointer ownership contracts in `FromGlibPtrFull`, null-pointer assumptions in private constructors, and exact length validation. Tests cover owned pointer adoption, hex/base64 round trips, invalid lengths/input, equality, display, and clone behavior, giving strong coverage for this low-level type.
