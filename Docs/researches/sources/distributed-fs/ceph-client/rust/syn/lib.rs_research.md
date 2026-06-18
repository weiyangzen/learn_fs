# Research: sources/distributed-fs/ceph-client/rust/syn/lib.rs

## Purpose
`lib.rs` is the crate root for the vendored Syn parser library. It documents Syn's procedural macro use cases, declares crate-level lints and feature gates, wires internal modules, and defines the top-level parsing entry points `parse`, `parse2`, `parse_str`, and `parse_file`.

## Important APIs, Types, And Functions
Most public API in this file is re-export orchestration. It re-exports AST nodes from `attr`, `data`, `derive`, `expr`, `file`, `generics`, `ident`, `item`, `lifetime`, `lit`, `mac`, `meta`, `op`, `pat`, `path`, `restriction`, `stmt`, and `ty` according to feature flags. It exposes `Error` and `Result` unconditionally, `punctuated` unconditionally, parser modules under `parsing`, and traversal modules `fold`, `visit`, and `visit_mut` from generated code when enabled. `__private` points to `export.rs` for non-public support.

The parsing entry points are thin wrappers: `parse<T>` accepts `proc_macro::TokenStream` when both `parsing` and `proc-macro` are enabled, `parse2<T>` accepts `proc_macro2::TokenStream`, and `parse_str<T>` parses string input. `parse_file` is specialized for full Rust files and preserves file-level affordances not handled by plain `FromStr`.

## Control Flow
Compilation is driven by `cfg` gates. Modules are only declared and re-exported when the corresponding features are enabled, which keeps procedural macro compile times lower for derive-only users. The generated `gen` module contains documentation and conditional declarations for traversal, clone, debug, equality, and hash support.

`parse_file` strips a UTF-8 byte order mark, detects a shebang beginning with `#!` unless it is an inner attribute (`#![...]` after whitespace), removes that shebang from the parsed content, delegates to `parse_str::<File>`, and restores the shebang onto the resulting `File`.

## State And Persistence Behavior
The crate root keeps no mutable runtime state. Its significant state is compile-time module availability determined by Cargo features. `parse_file` temporarily owns a shebang `String` and returns it in the AST. All parsing functions enforce complete consumption through the underlying `Parser` APIs.

## Dependencies And Integration Points
This file integrates Syn with `proc_macro` when enabled, `proc_macro2` for token-stream parsing, and feature-gated traversal/printing/parsing modules. It is the canonical integration surface for downstream macro crates because downstream code normally imports `syn::{parse_macro_input, DeriveInput, Item, Expr, Type, ...}` from these re-exports.

## Risks
Feature gates are the main risk. Moving a module or re-export across feature conditions can break downstream builds or unexpectedly increase compile cost. `parse_file` shebang detection must keep distinguishing real shebangs from inner attributes, otherwise valid crate files can parse incorrectly. Because this file is the public API hub, re-export changes are semver-sensitive even when internal modules remain unchanged.

## Test Signals
Tests should exercise representative feature matrices: default derive/parsing/printing, derive-only, full parsing, full printing, traversal features, extra traits, and proc-macro parsing. `parse_file` needs tests for BOMs, shebang-only files, shebang plus items, and inner attributes at the top of the file.
