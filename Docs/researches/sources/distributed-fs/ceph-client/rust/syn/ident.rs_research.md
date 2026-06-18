<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/ident.rs -->
# sources/distributed-fs/ceph-client/rust/syn/ident.rs

## Purpose

`ident.rs` centralizes Syn's identifier type alias, keyword-token conversions, simple identifier validation, and parsing/token-peeking behavior for identifiers. It re-exports `proc_macro2::Ident` as Syn's `Ident`, while adding Syn-specific parsing rules that reject Rust keywords where a normal identifier is required.

The file is small but important because identifier parsing appears in nearly every AST module. It distinguishes true identifiers from keywords, while still allowing helper APIs elsewhere to opt into broader parsing with `IdentExt::parse_any`.

## Important APIs, Types, and Functions

- `pub use proc_macro2::Ident` makes Syn's public `Ident` the proc-macro identifier type.
- The parsing-only hidden `Ident(marker: lookahead::TokenMarker) -> Ident` supports Syn's lookahead/token machinery for `Ident`.
- `ident_from_token!` implements `From<Token![...]> for Ident` for selected keyword tokens: `self`, `Self`, `super`, `crate`, and `extern`.
- `impl From<Token![_]> for Ident` converts underscore tokens into an identifier named `_`.
- `xid_ok(symbol: &str) -> bool` validates an ASCII-only identifier-like string for internal use.
- `accept_as_ident` rejects `_` and Rust keywords/reserved words when parsing a normal identifier.
- `impl Parse for Ident` parses a cursor identifier and rejects keywords with a targeted error message.
- `impl Token for Ident` implements lookahead peeking and display text for parser diagnostics.

## Control Flow

Parsing an `Ident` calls `input.step`, asks the cursor for `cursor.ident()`, and then validates the returned `proc_macro2::Ident` with `accept_as_ident`. If the cursor has no identifier, it reports `expected identifier`. If it has a keyword or `_`, it reports `expected identifier, found keyword ...`. Successful parsing returns the identifier and advances to the rest cursor.

Token peeking follows the same logic without consuming input: it calls `cursor.ident()` and returns true only when `accept_as_ident` accepts the result. The keyword-to-ident `From` impls bypass parsing and construct identifiers from token spans directly, which is useful when AST fields intentionally store keyword-shaped identifiers.

## State and Persistence Behavior

The module has no persistent mutable state. It preserves spans when converting tokens into identifiers by passing the token span into `Ident::new`. Parsing returns the identifier object from the cursor without altering its text or span.

`xid_ok` does not implement full Unicode XID. It intentionally checks ASCII alphabetic/number/underscore characters and requires the first character to be underscore or ASCII alphabetic.

## Dependencies and Integration Points

The file depends on `proc_macro2::Ident`, Syn token types, parse traits, parse buffers/cursors, and lookahead support. It is used by AST parsers throughout Syn wherever an ordinary identifier is expected. It also integrates with extension traits such as `IdentExt` in other modules when keywords, raw identifiers, or contextual identifiers need special handling.

## Risks and Edge Cases

- `accept_as_ident` contains a hard-coded keyword list based on the Rust 1.65 reference. New keywords or edition-specific changes require maintenance.
- Normal `Parse for Ident` rejects `_`, but some syntactic positions intentionally allow underscore and must use a different parser.
- `xid_ok` is ASCII-only despite its name. Using it as a full Rust identifier validator would reject valid Unicode identifiers.
- Keyword conversions create identifiers with keyword text. Those are valid for internal AST construction but should not be confused with ordinary parsed identifiers.
- Error wording treats `_` as a keyword-like rejection path, which is parser-facing behavior tests may depend on.

## Test Signals

Tests should cover parsing normal identifiers, rejecting each listed keyword and `_`, preserving spans in `From<Token![...]>`, and `Token for Ident` lookahead behavior. Additional tests should exercise contexts that intentionally accept keywords through `IdentExt::parse_any` so ordinary identifier parsing remains strict while special grammar positions remain usable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/ident.rs -->
