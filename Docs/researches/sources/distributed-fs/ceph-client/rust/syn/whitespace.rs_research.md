# sources/distributed-fs/ceph-client/rust/syn/whitespace.rs

Purpose: skips Rust whitespace and non-doc comments at the front of a string while preserving documentation comments as meaningful tokens for higher-level parsing.

Important APIs/types/functions: crate-private `skip(&str) -> &str` and helper `is_whitespace(char)`. The function recognizes line comments, nested block comments, empty block comments, ASCII whitespace, Unicode whitespace, and Rust-specific left-to-right and right-to-left marks.

Control flow: loops while the string begins with skippable content. It removes non-doc `//` comments, non-doc `/* ... */` comments with nesting, and whitespace bytes/chars. It returns an empty string for a line comment reaching EOF and returns the original suffix if a block comment is unterminated.

State and persistence: no persistent state; it only returns a slice into the caller's input.

Dependencies and integration: used by Syn scanners to normalize lookahead over lexical trivia without losing doc comments. It depends only on the standard library and Rust lexical rules.

Risks: comment classification must preserve `///`, `//!`, `/**`, and `/*!` doc comments. Unterminated block comments stop skipping so later parsing can report the real error. Unicode whitespace handling must stay aligned with rustc behavior.

Test signals: lexer tests for nested comments, doc-comment preservation, EOF comments, unterminated comments, CR/LF and tab whitespace, Unicode whitespace, and direction marks.
