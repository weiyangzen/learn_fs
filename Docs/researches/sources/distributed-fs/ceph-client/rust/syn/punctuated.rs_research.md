# sources/distributed-fs/ceph-client/rust/syn/punctuated.rs

## Purpose
`punctuated.rs` defines `Punctuated<T, P>`, Syn's shared representation for sequences of syntax nodes separated by punctuation, such as path segments, fields, generic bounds, call arguments, and pattern lists.

## Important APIs, types, and functions
Main types are `Punctuated<T, P>`, iterator types `Pairs`, `PairsMut`, `IntoPairs`, `IntoIter`, `Iter`, `IterMut`, private iterator adapters, and `Pair<T, P>`. Core methods include `new`, `is_empty`, `len`, `first`, `last`, `get`, `iter`, `pairs`, `push_value`, `push_punct`, `push`, `insert`, `pop`, `pop_punct`, `trailing_punct`, `empty_or_trailing`, and parsers `parse_terminated(_with)` and `parse_separated_nonempty(_with)`.

## Control flow
Internally, all punctuated elements except a possible final unpunctuated value are stored in `inner: Vec<(T, P)>`; the final value is `last: Option<Box<T>>`. `push_value` requires an empty or trailing state, while `push_punct` moves `last` into `inner`. Parsers alternate value parsing and punctuation parsing until stream end or missing separator.

## State and persistence behavior
State is entirely in-memory collection shape. The invariant is that `last == None` means empty or trailing punctuation, while `Some` means a final value without trailing punctuation.

## Dependencies and integration points
It depends on `Parse`, `Token`, `NoDrop`, `TrivialDrop`, standard iterators, and `quote::ToTokens` for printing. It is pervasive across Syn AST modules.

## Risks
Invariant violations panic in `push_value`, `push_punct`, `insert`, and `do_extend`. Iterator implementation uses boxed trait objects and `NoDrop`, so drop-safety assumptions matter. This vendored file appears to include duplicated/imbalanced source text around `PartialEq` and `PrivateIter` implementations, which is a serious compile/test signal for this checkout.

## Test signals
Tests should cover empty, singleton, trailing-punctuation, and non-trailing states; forward/backward iteration; mutable iteration; `Pair` conversion; parsing with and without trailing punctuation; `Extend<Pair>` panic after `Pair::End`; indexing; and feature-gated trait impl builds.
