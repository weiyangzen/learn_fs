# sources/cloud-native/ostree/rust-bindings/sys/src/manual.rs

Purpose: This hand-maintained Rust module supplements generated FFI with declarations that `gir` does not emit correctly or at all. In this snapshot it re-exports `libc::stat`.

Important APIs, types, and functions: The only public item is `pub use libc::stat;`, making the Unix `struct stat` type available to generated callback and function signatures in `lib.rs`, especially checkout filters and checksum-at APIs.

Control flow: There is no executable control flow. The generated `lib.rs` declares `mod manual; pub use manual::*;`, so the `stat` name is pulled into the `ostree_sys` public namespace before it is used in FFI signatures.

State and persistence behavior: None. This file carries type identity only.

Dependencies and integration points: It depends on `libc` and the target being Unix-compatible for `stat`. It is paired conceptually with `sys/tests/manual.h`, which provides manual C-side compatibility definitions used by ABI tests.

Risks: A wrong `stat` type would corrupt ABI for callbacks or functions that pass `struct stat` across FFI. Platform assumptions matter because `stat` layout is libc and target dependent.

Test signals: `sys/tests/abi.rs` compiles only on Unix and uses generated FFI that references `stat`; successful ABI test compilation is the main signal that this manual export is sufficient.
