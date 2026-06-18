# sources/distributed-fs/ceph-client/tools/perf/util/demangle-rust-v0.c

## Purpose
This file is a C translation of Rust `rustc-demangle` support used by perf to recognize and display Rust legacy `_ZN...E` and v0 `_R...` symbol names. It keeps close upstream parity, exposes only the public functions declared in `demangle-rust-v0.h`, and otherwise implements a private parser/printer pipeline for paths, types, constants, lifetimes, backreferences, punycode identifiers, and suffix handling.

## Important APIs, Types, And Functions
The public entry points are `rust_demangle_demangle()`, `rust_demangle_display_demangle()`, and `rust_demangle_is_known()`. Internal state is split between `struct parser` for symbol traversal and recursion depth, `struct printer` for formatted output and overflow tracking, `struct demangle_v0`, `struct demangle_legacy`, and `struct ident`. Core helpers include `rust_demangle_v0_demangle()`, `rust_demangle_v0_display_demangle()`, `rust_demangle_legacy_demangle()`, `rust_demangle_legacy_display_demangle()`, `printer_print_path()`, `printer_print_type()`, `printer_print_const()`, `parser_backref()`, and `display_ident()`.

## Control Flow
`rust_demangle_demangle()` first strips ThinLTO `.llvm.<hex>` suffixes, tries legacy parsing, then v0 parsing, and otherwise marks the symbol unknown. Both parsers validate ASCII, prefixes, length encodings, and terminal structure before saving references into the original input. Display dispatches by style: unknown symbols are copied raw, legacy elements are decoded and joined with `::`, and v0 symbols are recursively printed through path/type/const grammar functions. After the main symbol is printed, valid symbol-like suffixes are appended.

## State, Dependencies, And Integration
The demangle result stores borrowed pointers into the caller's symbol string; callers must keep the input stable until display completes. Output is caller-owned and guarded by `OVERFLOW_MARGIN`, while parser recursion is bounded by `MAX_DEPTH`. Dependencies are intentionally small: libc string/stdio/stdint helpers plus the public header. Integration is via perf symbol display paths that need Rust demangling without pulling Rust code into perf.

## Risks And Test Signals
Key risks are divergence from upstream `rustc-demangle`, accidental use-after-free of borrowed string slices, output explosion from recursive/backreference-heavy v0 names, and edge cases in UTF-8, punycode, or const-string escaping. Tests should cover legacy and v0 valid symbols, unknown symbols, LLVM suffix stripping, alternate formatting without hashes/types, too-small output buffers returning `OverflowOverflow`, non-ASCII rejection for mangled payloads, recursion-limit handling, and malformed lengths/backrefs/hex nibbles.
