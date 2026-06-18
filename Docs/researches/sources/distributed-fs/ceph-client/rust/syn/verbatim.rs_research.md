# sources/distributed-fs/ceph-client/rust/syn/verbatim.rs

Purpose: reconstructs an uninterpreted `TokenStream` between two Syn parser positions for syntax that should be preserved as verbatim rather than parsed into a structured AST node.

Important APIs/types/functions: exposes crate-private `between(begin, end) -> TokenStream`. It uses `ParseStream::cursor`, `cursor.token_tree`, `cursor.group(Delimiter::None)`, `buffer::same_buffer`, and `buffer::cmp_assuming_same_buffer`.

Control flow: the function asserts both cursors belong to the same buffer, walks token trees from `begin` to `end`, and extends a new `TokenStream` with each token. If a token would cross the end boundary because of a none-delimited group, it enters that group and continues; any other boundary crossing panics.

State and persistence: no persistent state. The returned token stream is a copied representation of the source range.

Dependencies and integration: used by parsers such as `ty.rs` to preserve unmodeled syntax like unsupported type forms or special bare function argument spellings. Relies on Syn's buffer cursor invariants and `proc_macro2` token streams.

Risks: incorrect begin/end pairing can assert or panic. Transparent `Delimiter::None` handling is intentionally narrow; changes in parser transparency rules could expose boundary bugs.

Test signals: tests should exercise verbatim fallback for syntax crossing none-delimited groups, plus malformed cursor-pair debug assertions through Syn parser tests.
