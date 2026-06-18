# sources/cloud-native/ostree/rust-bindings/sys/tests/constant.c

Purpose: This generated C fixture prints libostree constant names and values so `abi.rs` can compare them against Rust constants in `ostree_sys`.

Important APIs, types, and functions: It includes `manual.h` and `<stdio.h>`. The `PRINT_CONSTANT` macro emits `<name>;<value>\n` using C11 `_Generic` to select a printf format for strings, characters, signed and unsigned integer widths, and floating types. `main` prints OSTree checksum flags, GVariant format strings, commit metadata keys, deployment states, diff flags, GPG errors and signature attributes, object types, repo checkout/commit/list/prune/pull/remote/verify flags, SELinux flags, SHA256 lengths, signing names, static delta options, sysroot flags, and tree/summary format strings.

Control flow: `main` is a straight-line list of `PRINT_CONSTANT(...)` invocations followed by `return 0`. No branching occurs beyond format selection in `_Generic`.

State and persistence behavior: The fixture has no persistent state. Its only side effect is stdout.

Dependencies and integration points: It depends on libostree C headers through `manual.h`, on C11 for `_Generic`, and on the exact output ordering expected by `RUST_CONSTANTS` in `abi.rs`.

Risks: `_Generic` coverage must match the types of printed constants; unsupported types would fail to compile. Order drift between this file and `RUST_CONSTANTS` causes false mismatches. Backfilled constants in `manual.h` can hide older-header gaps intentionally, so tests verify compatibility behavior rather than only upstream header declarations.

Test signals: When compiled and run by `abi.rs`, each stdout row becomes an assertion target for the Rust binding constant with the same textual name.
