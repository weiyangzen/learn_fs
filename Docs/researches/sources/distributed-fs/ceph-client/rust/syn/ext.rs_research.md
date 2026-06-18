# sources/distributed-fs/ceph-client/rust/syn/ext.rs

## Purpose

This file defines extension methods for foreign types, currently `proc_macro2::Ident`. It adds Syn-specific identifier parsing and normalization needed by macro DSLs and Rust grammar code.

## Important APIs, Types, and Functions

- `IdentExt`: sealed trait implemented only for `proc_macro2::Ident`.
- `IdentExt::parse_any`: parses any identifier, including Rust keywords.
- `IdentExt::peek_any`: associated `PeekFn` value used as `input.peek(Ident::peek_any)`.
- `IdentExt::unraw`: strips a leading `r#` from raw identifiers while preserving span.
- `impl Peek for private::PeekFn`: connects the peek function to a custom token marker.
- `impl CustomToken for private::IdentAny`: peeks `cursor.ident()` and displays as `identifier`.
- Private sealed module: `Sealed`, `PeekFn`, and `IdentAny`.

## Control Flow

`parse_any` uses `ParseStream::step` and directly asks the cursor for an identifier. Since `cursor.ident()` returns identifiers regardless of keyword status, this bypasses normal keyword exclusion. `peek_any` works through Syn's `Peek`/`CustomToken` infrastructure: lookahead invokes `IdentAny::peek`, which checks whether the cursor has any identifier. `unraw` converts the identifier to a string, strips `r#` if present, and creates a new `Ident` with the same span; otherwise it clones the original.

## State and Persistence

No persistent state exists. `unraw` creates a new identifier only when necessary. `PeekFn` is zero-sized and `Copy`.

## Dependencies and Integration Points

The module depends on `buffer::Cursor`, `error::Result`, `ParseStream`, `Peek`, `lookahead::Sealed`, `CustomToken`, and `proc_macro2::Ident`. It is used by parsers that accept keywords as identifiers, including field parsing and expression/path grammar. It also supports macro authors building DSLs with keyword-like names.

## Risks and Edge Cases

`parse_any` intentionally accepts Rust keywords, so parsers must only use it in positions where keywords are valid as names. `unraw` preserves span but changes textual identity; generated identifiers can become Rust keywords if reused without raw escaping, which is intended for foreign-language interop but must be used knowingly. The trait is sealed, so downstream crates cannot extend this pattern to other identifier-like types.

## Test Signals

No inline tests appear here. Useful tests include parsing ordinary identifiers, Rust keywords, and raw identifiers through `parse_any`; peeking without consuming; and verifying `unraw` output and span preservation for `x`, `move`, and `r#move`.
