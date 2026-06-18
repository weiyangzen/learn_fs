<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/group.rs -->
# sources/distributed-fs/ceph-client/rust/syn/group.rs

## Purpose

`group.rs` provides Syn's low-level parsing helpers for delimited token groups. It backs the public `parenthesized!`, `braced!`, and `bracketed!` macros used throughout parser implementations to consume a delimiter pair and expose the nested tokens as a new `ParseBuffer`. It also supports invisible delimiter groups for full/derive internals.

The module bridges `proc_macro2` cursor groups and Syn parse streams. It preserves delimiter spans in token marker types while giving downstream parsers a scoped buffer over group contents.

## Important APIs, Types, and Functions

- `Parens<'a>`, `Braces<'a>`, and `Brackets<'a>` are hidden structs containing the parsed delimiter token and nested `ParseBuffer`.
- `Group<'a>` is a hidden full/derive-gated struct for `Delimiter::None` invisible groups.
- `parse_parens`, `parse_braces`, and `parse_brackets` parse the corresponding delimiter and return the hidden wrapper.
- `parse_group` parses an invisible group and converts its `DelimSpan` with `span.join()` into `token::Group`.
- `parse_delimited` is the common implementation over a requested `proc_macro2::Delimiter`.
- `parenthesized!`, `braced!`, and `bracketed!` are exported macros that bind a caller-named content buffer and return the delimiter token, or return the parse error from the enclosing parser.

## Control Flow

All public helpers call `parse_delimited`. That function uses `input.step` to inspect the current cursor. If `cursor.group(delimiter)` succeeds, it receives the nested content cursor, delimiter span, and rest cursor. It derives a parsing scope from `span.close()`, advances the nested cursor relative to the outer cursor with `advance_step_cursor`, carries forward the parse buffer's unexpected-token state, and constructs a new nested `ParseBuffer`.

If no matching group is present, `parse_delimited` returns a cursor error with a delimiter-specific message such as `expected parentheses` or `expected square brackets`.

The exported macros wrap this in parser-friendly syntax. On success they assign `parens.content`, `braces.content`, or `brackets.content` to the caller's variable and evaluate to the delimiter token. On failure they immediately return `Err(error)` from the caller.

## State and Persistence Behavior

The module does not keep global state. It creates nested parse buffers that borrow from the input token buffer lifetime. Delimiter token structs store span information so parsed AST nodes can later print or report errors with the original delimiter spans.

The nested `ParseBuffer` is scoped to the group's close delimiter. Parsing inside the content buffer does not consume tokens after the group in the outer buffer; `input.step` returns `rest` as the outer cursor continuation.

## Dependencies and Integration Points

The code depends on `crate::parse::ParseBuffer`, parse cursor helpers, `crate::error::Result`, Syn token marker types, `proc_macro2::Delimiter`, and `proc_macro2::extra::DelimSpan`.

Integration is pervasive across Syn parsing. AST parsers use `parenthesized!` for tuple fields, function argument lists, and grouped expressions; `braced!` for item bodies and struct fields; and `bracketed!` for attributes, array types, and array expressions. The hidden parse functions are re-exported through Syn's private module for macro expansion.

## Risks and Edge Cases

- The macros return from the enclosing parser on error. They must only be used in functions returning Syn's `Result`.
- Delimiter type must match exactly. Invisible groups are handled separately through `parse_group`.
- Correct nested buffer scope depends on `span.close()` and cursor advancement. Mistakes here would leak tokens across delimiters or produce confusing errors.
- The helper exposes group contents but does not enforce that the content buffer is fully consumed. Individual parsers remain responsible for consuming expected inner syntax.
- These APIs are hidden/internal even though the macros are public; changing wrapper fields or private paths can break macro expansion.

## Test Signals

Parser tests that cover custom `Parse` implementations using `parenthesized!`, `braced!`, and `bracketed!` are direct signals. Error snapshot tests should verify wrong-delimiter messages and spans. Round-trip tests for attributes, tuple structs, braced structs, arrays, function signatures, and nested groups exercise integration. Full/derive feature builds should include invisible group handling where those AST nodes are enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/group.rs -->
