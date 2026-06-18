# Research: sources/distributed-fs/ceph-client/rust/syn/macros.rs

## Purpose
`macros.rs` contains local macro definitions that generate much of Syn's AST boilerplate. It centralizes struct/enum declarations, enum-to-struct `From` impls, `ToTokens` forwarding for enum wrappers, doc-only visibility tweaks, keyword validation, and docsrs-specific return type selection.

## Important APIs, Types, And Functions
`ast_struct!` declares AST structs and can create placeholder non-`full` versions for `#full` structs. `ast_enum!` declares AST enums under the appropriate feature gates. `ast_enum_of_structs!` declares an enum, generates `From<Member>` conversions through `ast_enum_of_structs_impl!`, and generates `ToTokens` forwarding when `printing` is enabled. `pub_if_not_doc!` exposes hidden parser marker functions publicly outside docs while keeping them crate-private during documentation builds. `return_impl_trait!` switches between a concrete return type for normal builds and an `impl Trait` signature for docsrs.

## Control Flow
These macros expand at compile time only. `generate_to_tokens!` recursively accumulates match arms for enum variants, ignoring fieldless variants and forwarding single-member variants to the contained node's `ToTokens`. `check_keyword_matches!` forces macro invocations to use the expected literal keywords (`pub`, `struct`, `enum`) and prevents accidental syntactic drift.

## State And Persistence Behavior
The file has no runtime state. Its "state" is compile-time generated code conditioned on crate features. Placeholder structs for non-`full` builds use `PhantomData<proc_macro2::Span>` to prevent construction while keeping type names available for selected feature combinations.

## Dependencies And Integration Points
Every AST module in this subset relies on these macros. They integrate with `quote::ToTokens`, `proc_macro2::TokenStream`, docsrs cfgs, and Syn's feature gating policy. The generated `From` impls and printing impls are part of the ergonomic public surface even though the macros are internal.

## Risks
Macro changes have wide blast radius. A small change can alter public type layout, generated trait impls, docs visibility, or feature-gated availability across the crate. The recursive token-generation macro assumes enum variants are either fieldless or single-member wrappers; adding a differently shaped enum through this macro would require macro changes. Placeholder non-`full` structs intentionally panic on printing, so they must remain unreachable under valid feature combinations.

## Test Signals
Tests should compile representative AST modules under feature combinations, verify `From` conversions for enum wrapper variants, verify generated `ToTokens` forwarding, run docs builds, and include trybuild-style checks for public visibility under docs and non-docs builds.
