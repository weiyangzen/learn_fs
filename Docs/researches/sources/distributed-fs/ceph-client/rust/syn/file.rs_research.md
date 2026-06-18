# sources/distributed-fs/ceph-client/rust/syn/file.rs

## Purpose

This file defines Syn's AST node for a complete Rust source file. It captures an optional shebang string, inner file attributes, and the sequence of top-level items.

## Important APIs, Types, and Functions

- `File`: complete Rust file with `shebang: Option<String>`, `attrs: Vec<Attribute>`, and `items: Vec<Item>`.
- `parsing::impl Parse for File`: parses inner attributes and then parses items until the stream is empty.
- `printing::impl ToTokens for File`: prints inner attributes and items.

## Control Flow

`File::parse` constructs a `File` with `shebang: None`, reads inner attributes with `Attribute::parse_inner`, then loops while the input is not empty and pushes each parsed `Item` into a vector. Shebang handling is not performed here; it is expected to be handled by the higher-level `parse_file` entry point before token parsing. Printing appends inner attributes and then all items.

## State and Persistence

`File` stores only parsed syntax in memory. There is no file I/O despite the type name; callers are responsible for reading source text and invoking `parse_file` or parser APIs. `shebang` is a string field populated outside this `Parse` impl.

## Dependencies and Integration Points

The module depends on `Attribute` and `Item`. It is the root AST for full-file parsing and integrates with `crate::parse_file`, `Parse`, `quote::ToTokens`, and the item parser. Downstream tools use it for source-to-source analysis and transformations.

## Risks and Edge Cases

The parse impl sets `shebang` to `None`, so using `input.parse::<File>()` directly on token streams cannot recover a shebang. The item loop depends on each `Item` parser consuming input; if an item parser ever accepted empty input it would risk an infinite loop, but Syn item parsers should not. Printing omits shebang, consistent with token-stream printing but relevant for exact source regeneration.

## Test Signals

No inline tests appear here. Useful tests should cover parse_file shebang preservation, direct `Parse` shebang absence, inner attributes before items, empty files, item sequences, and token printing of attributes/items.
