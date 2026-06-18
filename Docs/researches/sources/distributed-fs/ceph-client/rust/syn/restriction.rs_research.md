# sources/distributed-fs/ceph-client/rust/syn/restriction.rs

## Purpose
`restriction.rs` defines visibility-related AST nodes and parsing/printing for `pub`, restricted `pub(...)`, and inherited visibility. It also reserves `FieldMutability` for future field mutability restrictions.

## Important APIs, types, and functions
Important types are `Visibility`, `VisRestricted`, and `FieldMutability`. `Visibility::parse` handles normal visibility parsing and empty none-delimited groups from `$:vis`. `Visibility::parse_pub` recognizes `pub`, `pub(crate)`, `pub(self)`, `pub(super)`, and `pub(in path)`. `Visibility::is_some` is available under `full`.

## Control flow
Parsing first detects an empty invisible group and returns `Inherited`. For `pub`, it speculatively parses parenthesized content. If the content is `crate`, `self`, or `super` and fully consumed, it records a restricted visibility without `in`. If it starts with `in`, it parses a module-style path. Otherwise, it returns plain public visibility.

## State and persistence behavior
No persistent state. Speculative parser state is reconciled with `advance_to` only after a restricted form is confirmed.

## Dependencies and integration points
It depends on paths, tokens, identifiers, `Speculative`, and parse APIs. Printing integrates with `path::printing::print_path` using `PathStyle::Mod`.

## Risks
The parser intentionally avoids misreading tuple fields like `pub (crate::A, crate::B)` as restricted visibility; this is a regression-prone ambiguity. The TODO for RFC 3323 marks future expansion risk. Printing does not automatically insert `in` for arbitrary paths when `in_token` is absent.

## Test signals
Tests should cover inherited, empty `$:vis` group, all restricted forms, `pub(in a::b)`, tuple-field ambiguity, and printing of restricted paths.
