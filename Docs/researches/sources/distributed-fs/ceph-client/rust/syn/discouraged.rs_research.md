# sources/distributed-fs/ceph-client/rust/syn/discouraged.rs

## Purpose

This file exposes niche parsing extensions that are intentionally separated from the main parsing API: speculative parsing commit support and delimiter-agnostic group parsing. The module documentation and trait names signal that these tools are powerful but can degrade diagnostics when overused.

## Important APIs, Types, and Functions

- `Speculative`: extension trait with `advance_to(&self, fork: &Self)` for committing a forked `ParseStream` back into the original stream.
- `impl Speculative for ParseBuffer`: validates fork ancestry/scope, propagates unexpected-token diagnostic state, and updates the main cursor.
- `AnyDelimiter`: extension trait with `parse_any_delimiter` returning `(Delimiter, DelimSpan, ParseBuffer)`.
- `impl AnyDelimiter for ParseBuffer`: uses `Cursor::any_group` to parse parentheses, brackets, braces, or invisible delimiters uniformly.

## Control Flow

`advance_to` first checks that `self.cursor()` and `fork.cursor()` are in the same scope. If not, it panics because the fork did not originate from the advancing stream. It then compares the shared unexpected-token cells of the two streams. If the fork has an unexpected token and the original does not, it copies that unexpected value to the original. If both are unset, it chains the fork's unexpected cell to the original and replaces the fork's root unexpected pointer to avoid leaking top-level fork errors. Finally, it writes the fork cursor into the original parse buffer cell using a transmute to the buffer's internal static cursor representation.

`parse_any_delimiter` runs a parser step. If the cursor points at any token group, it computes the group close span, advances a nested cursor into the content, shares the current unexpected state, creates a nested `ParseBuffer`, and returns the delimiter metadata plus rest cursor. If no group is present, it returns a cursor error.

## State and Persistence

The key state is parse-buffer cursor position and shared diagnostic state held in `Rc<Cell<Unexpected>>`. `advance_to` mutates the original parse buffer cursor and may relink unexpected-token state. There is no persistent storage. The unsafe transmute is local but relies on ParseBuffer's invariant that the cursor cell owns a lifetime-erased cursor.

## Dependencies and Integration Points

The module depends on `buffer::Cursor`, `ParseBuffer`, `inner_unexpected`, `Unexpected`, `proc_macro2::Delimiter`, `proc_macro2::extra::DelimSpan`, `Rc`, `Cell`, and low-level parse constructors (`advance_step_cursor`, `get_unexpected`, `new_parse_buffer`). It is used by parsers that need fork/try/commit behavior, including expression and data parsing branches elsewhere in Syn.

## Risks and Edge Cases

The main risk is diagnostic quality: a failed speculative branch may cause the parser to report fallback errors rather than the branch that consumed more meaningful input. `advance_to` panics if the fork is unrelated or from a different scope. The unsafe cursor lifetime erasure must remain aligned with `ParseBuffer` internals. Incorrect unexpected-state propagation could produce confusing or stale errors.

## Test Signals

No inline unit tests appear here. The doc example demonstrates speculative turbofish parsing. Useful tests should cover successful fork commits, invalid fork panic behavior, preservation of unexpected-token diagnostics through nested groups, and `parse_any_delimiter` for all delimiter kinds including invisible groups.
