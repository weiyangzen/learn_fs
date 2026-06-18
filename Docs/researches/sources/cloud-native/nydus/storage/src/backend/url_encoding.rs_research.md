# sources/cloud-native/nydus/storage/src/backend/url_encoding.rs

## Purpose
`url_encoding.rs` provides a compact percent-encoding helper for backend URL components. It is ported from `rust_urlencoding` and kept compatible with older Rust versions. The encoder leaves only ASCII alphanumerics and `-`, `_`, `.`, `~` unescaped.

## Important APIs, Types, And Functions
`Encoded<Str>` is a transparent wrapper implementing `Display` for on-the-fly encoding without requiring an allocation. It offers `new`, `to_str`, `to_string`, `write`, and `append_to`; `Encoded::str` helps type inference for `&str`. Free functions `encode(&str)` and `encode_binary(&[u8])` return `Cow<str>`, borrowing when the input is already safe ASCII and allocating only when escaping is needed. `append_string`, `encode_into`, and `to_hex_digit` are internal helpers.

## Control Flow
`encode_binary` creates an output buffer and calls `append_string` with `may_skip=true`. `encode_into` scans leading safe bytes, writes them as unchecked UTF-8 only after confirming they are safe ASCII, then percent-encodes one unsafe byte at a time using uppercase hex digits. If the entire input is safe and skipping is allowed, it returns `Ok(true)` so `encode_binary` can return `Cow::Borrowed`.

## State And Persistence Behavior
The module is stateless. It allocates only for encoded output or writer/string append targets and has no shared state, IO state, or persistence.

## Dependencies And Integration Points
It depends only on standard library `Cow`, formatting, IO, and UTF-8 primitives. Backend modules can use it for object keys, query parameters, or path fragments where RFC3986-style percent encoding is required.

## Risks And Edge Cases
The encoder operates on bytes and assumes UTF-8 only when returning borrowed safe ASCII or writing safe fragments; non-UTF8 bytes are always escaped. It does not implement form encoding: spaces become `%20`, not `+`. It encodes `/`, `:`, `@`, and other reserved characters, so callers must choose correctly between encoding a path segment and a whole URL/path. The generic `impl<String: AsRef<[u8]>> Display` shadows the common `String` name as a type parameter, which is legal but slightly confusing.

## Test Signals
Tests cover borrowed output for safe ASCII, reserved character escaping, non-UTF8 byte encoding, consistency between helper methods and `Display`, and append/write behavior.
