# Research: sources/distributed-fs/ceph-client/rust/syn/meta.rs

## Purpose
`meta.rs` provides parsing utilities for structured attribute contents such as `#[tea(kind = "EarlGrey", hot, with(sugar))]`. It is focused on conventional nested meta syntax and is available when parsing plus `full` or `derive` support is enabled.

## Important APIs, Types, And Functions
`parser(logic)` adapts a `FnMut(ParseNestedMeta) -> Result<()>` callback into a `Parser<Output = ()>` usable with `parse_macro_input!` for attribute macro arguments. `ParseNestedMeta<'a>` exposes the parsed `path` and remaining `input` for one property. `value()` consumes `=` and returns the same parse stream for parsing the value. `parse_nested_meta()` parses parenthesized nested content using the same convention. `error(msg)` creates a span covering the property path through the latest consumed token. The internal `parse_nested_meta` loop handles comma-separated properties and trailing commas. `parse_meta_path` parses paths that accept keywords as identifiers and emits tailored errors for literals or other unexpected tokens.

## Control Flow
The top-level parser returns `Ok(())` on empty input; otherwise it loops through `parse_nested_meta`. Each iteration parses a meta path, calls user logic with the current parse stream, then requires a comma unless the input is empty. Nested lists are parsed by `parenthesized!` and recursively applying the same loop. User logic is responsible for interpreting `path`, deciding whether to call `value`, parse a list, or reject the property.

## State And Persistence Behavior
There is no persistent state. Mutable state is normally held by the user's closure, as shown in the examples that fill option and vector fields. `ParseNestedMeta` borrows the active parse stream, so it is a transient view into the parser cursor.

## Dependencies And Integration Points
This module integrates with `Attribute::parse_nested_meta`, `parse_macro_input!`, Syn's `Parser` trait, paths, literals, punctuation, and error construction. It uses `IdentExt::parse_any` so keywords can appear in meta paths, matching Rust attribute conventions.

## Risks
`parser` is explicitly less precise for non-attribute-macro contexts because rustc conceals surrounding delimiter spans for proc-macro attribute arguments. Callers should prefer `Attribute::parse_nested_meta` when they have a full `Attribute`. The utility only fits conventional structured attributes; arbitrary token grammars inside parentheses should parse the exposed `ParseStream` directly. Error span construction depends on `prev_span`, so callbacks that parse far ahead before calling `error` intentionally produce wider diagnostics.

## Test Signals
Tests should cover empty args, simple flags, name-value pairs, nested lists, trailing commas, keyword path segments, leading colons and path separators, unsupported literals in path position, custom errors after value parsing, and comparison between `parser` and `Attribute::parse_nested_meta` span quality.
