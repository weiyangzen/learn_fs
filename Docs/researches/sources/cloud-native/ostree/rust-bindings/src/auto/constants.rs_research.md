# sources/cloud-native/ostree/rust-bindings/src/auto/constants.rs

Purpose: Generated Rust constants exposing libostree string constants as `&glib::GStr`.

Important APIs: Constants include GVariant format strings for commits, dirmeta, filemeta, GPG keys, summary, summary signatures, and trees; commit metadata keys such as version, end-of-life, ref/collection binding, architecture, source title; deployment and repo metadata keys; signing engine names; and `PATH_BOOTED`.

Control flow and state: There is no runtime control flow beyond unsafe construction of static `GStr` references from nul-terminated FFI constants. Feature gates expose constants only for libostree versions that define them.

Dependencies and integration points: Depends on `ostree-sys` constants and GLib `GStr`. Used across Rust bindings when constructing metadata dictionaries, interpreting commit metadata, or selecting signature engines.

Risks: `from_utf8_with_nul_unchecked` assumes the FFI constants are valid UTF-8 and nul-terminated. That is appropriate for libostree constants but unsafe if GIR/sys metadata is wrong. Feature gates must match symbol availability to avoid link errors.

Test signals: Compile and link under minimum and feature-enabled libostree versions; metadata integration tests should use constants rather than duplicated string literals.
