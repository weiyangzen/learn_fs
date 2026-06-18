# sources/distributed-fs/ceph-client/rust/quote/ext.rs

## Purpose

This file defines `TokenStreamExt`, the sealed extension trait that makes implementing `ToTokens` ergonomic by appending token trees, sequences, separated lists, and terminated lists.

## Important APIs, types, and functions

`append` extends a stream by one `Into<TokenTree>` value. `append_all` calls `ToTokens` for every item. `append_separated` writes items with an operator between them. `append_terminated` writes each item followed by a terminator. The private `Sealed` trait prevents external implementations.

## Control flow

All methods are linear iteration over provided inputs. `append_separated` uses `enumerate` to suppress the separator before the first item; `append_terminated` always appends the terminator after every item.

## State and persistence behavior

The only state mutation is appending into the caller-provided `proc_macro2::TokenStream`.

## Dependencies and integration points

It depends on `quote::ToTokens`, `proc_macro2::{TokenStream, TokenTree}`, and `core::iter`. It is re-exported from `quote/lib.rs` and used by downstream `ToTokens` implementations and quote runtime helpers.

## Risks and test signals

Risks are separator placement regressions, unintended external trait impls, and accidental extra clones for large streams. Tests should verify empty, single, and multi-item sequences for all helper methods and downstream syntax printing that relies on punctuation placement.
