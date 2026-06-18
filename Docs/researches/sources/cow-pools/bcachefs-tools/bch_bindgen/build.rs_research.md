# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/build.rs

- Build script that generates Rust bindings and companion typed helpers from bcachefs C headers.
- Implements an x-macro parser that extracts entries from macro definitions while respecting nested parentheses.
- Generates superblock field traits, string tables, persistent counter metadata, extent-entry sizing, and typed bkey dispatch enums/accessors.
- Configures bindgen against `libbcachefs_wrapper.h` with target triple, include paths, allowlists/blocklists, enum handling, opaque/no-copy types, static-inline wrappers, and parse callback fixes for macro constants.
- Compiles bindgen-generated static-inline C wrappers with `cc` and emits Debian `dh-cargo` built-using metadata.
- Watches `../fs`, `../c_src`, and `../include` headers/sources for rebuilds.
- Generates a separate keyutils binding from `keyutils_wrapper.h`.
- Post-processes generated bindings to repair Rust layout for C packed/aligned structs, including 32-bit align(8) fixes for bkey-containing structs.
