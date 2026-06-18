# sources/distributed-fs/ceph-client/rust/proc-macro2/parse.rs

## Purpose

This file implements the fallback lexer/parser that turns Rust source text into fallback `TokenStream` values. It recognizes whitespace, comments, doc comments, groups, identifiers, raw identifiers, punctuation, strings, byte strings, C strings, characters, integers, floats, lifetimes, and selected rustc error placeholders.

## Important APIs, types, and functions

`Cursor` is the immutable parsing cursor with `rest` and optional `off` character offset. `Reject` is the local parse-failure sentinel. `token_stream` is the top-level parser that builds streams using `TokenStreamBuilder` and a delimiter stack. `leaf_token` tries literal, punctuation, identifier, and `(/*ERROR*/)` recognition. Literal helpers cover cooked/raw strings, byte strings, C strings, byte and char literals, numeric literals, suffixes, raw-string delimiters, escapes, Unicode escapes, and line continuations. `doc_comment` rewrites doc comments into `#[doc = "..."]` token trees.

## Control flow

`token_stream` loops until input is exhausted. Each iteration skips non-doc whitespace/comments, translates doc comments first, then handles opening delimiters by pushing a frame, closing delimiters by popping and creating a `Group`, or leaf tokens by parsing and assigning spans. Unbalanced or mismatched delimiters return `LexError`. Literal parsing is ordered to avoid misclassifying literal prefixes as identifiers. Punctuation determines `Joint` spacing by looking ahead to the next punctuation, with special handling for apostrophes and lifetimes.

## State and persistence behavior

Parser state is local: the current `Cursor`, output builder, delimiter stack, and optional span offsets. It persists parsed tokens into fallback `TokenStream` objects. With `span_locations`, offsets advance by character count rather than bytes, while spans store `lo`/`hi` positions for later location mapping.

## Dependencies and integration points

It depends on fallback token types and validation helpers (`is_ident_start`, `is_ident_continue`), public facade enums (`Delimiter`, `Spacing`, `TokenTree`), and `proc_macro2::Punct`. It is called by fallback `TokenStream::from_str_checked` and literal parsing.

## Risks and test signals

Risks include Rust lexical grammar drift, nested block comment edge cases, doc-comment span/content bugs, raw string delimiter limits, C string NUL handling, Unicode escape validation, float/int boundary cases such as ranges and suffixes, apostrophe/lifetime ambiguity, and byte-vs-character offset mismatch. Tests should include round-trip parsing, Rust lexer fixture comparisons, doc comment expansion, malformed literal failures, nested delimiter errors, and span-location assertions.
