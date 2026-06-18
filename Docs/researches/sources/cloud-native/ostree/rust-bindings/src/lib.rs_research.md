# sources/cloud-native/ostree/rust-bindings/src/lib.rs

## sources/cloud-native/ostree/rust-bindings/src/lib.rs

Crate root for the safe Rust `ostree` bindings. It documents libostree's purpose, enables docs cfg when requested, denies unused must-use values, warns on missing docs and broken links, re-exports `ffi`, `gio`, `glib`, and `libc::AT_FDCWD`, includes generated GIR bindings under `auto`, and layers handwritten modules on top.

Important integration behavior is the public export surface: generated functions/types are re-exported first, then handwritten extensions such as `Checksum`, core variant aliases, `SysrootBuilder`, repo helpers, checkout options, transaction stats, SELinux cleanup, and option structs. Feature gates mirror libostree version gates so downstream code can compile against selected API levels. The `prelude` re-exports generated traits plus `gio`/`glib` preludes.

State and persistence are not implemented here, but this file controls which APIs callers see and how generated and handwritten modules compose. Risks are export conflicts, feature-gate mismatches, and public API stability. Test integration is through `#[cfg(test)] mod tests`.
