# sources/distributed-fs/ceph-client/rust/syn/attr.rs

## Purpose

This file defines Syn's attribute AST and parsing/printing support for Rust attributes and doc comments.

## Important APIs, types, and functions

`Attribute` stores `#`, `AttrStyle`, bracket tokens, and `Meta`. `Attribute::path`, `parse_args`, `parse_args_with`, `parse_nested_meta`, `parse_outer`, and `parse_inner` are the main APIs. `AttrStyle` distinguishes outer and inner attributes. `Meta` has `Path`, `List`, and `NameValue` variants with `path`, `require_path_only`, `require_list`, and `require_name_value`. `MetaList` stores path, delimiter, and tokens and can parse arguments or nested meta. `FilterAttrs` filters outer/inner attrs for printing.

## Control flow

Outer and inner parsers loop while `#` or `#!` tokens are present, parse bracket contents, and parse `Meta`. `parse_meta_after_path` selects list, name-value, or bare path based on following delimiters or `=`. Name-value parsing preserves old literal-only behavior by first forking and accepting a lone literal as `Expr::Lit`; nested attributes inside attributes are rejected. Printing reconstructs `#`, optional `!`, brackets, paths, delimiters, and values.

## State and persistence behavior

Attributes persist parsed syntax tree state: punctuation tokens and spans, style, path, raw list token streams, delimiters, and expression values. `MetaList::parse_args_with` reparses stored tokens under the close-delimiter span for better errors.

## Dependencies and integration points

It depends on Syn expression, macro delimiter, meta parsing, parse streams, paths, punctuation tokens, `proc_macro2::TokenStream`, and `quote::ToTokens` under printing. It integrates with every Syn item/field/variant parser that stores attributes and with macro crates that parse structured attribute arguments.

## Risks and test signals

Risks include accepting invalid outermost keyword paths, poor error spans for empty or wrong-form attributes, incorrect doc-comment equivalence, nested attribute rejection regressions, arbitrary token preservation in lists, and print/parse round-trip drift. Tests should cover outer/inner attrs, doc comments, `Meta::Path/List/NameValue`, literal and expression name-values, `parse_nested_meta`, delimiter variants, malformed attributes, and printing filters.
