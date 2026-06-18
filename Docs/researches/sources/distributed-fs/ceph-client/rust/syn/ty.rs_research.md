# sources/distributed-fs/ceph-client/rust/syn/ty.rs

Purpose: defines Syn's Rust type syntax tree and the parser/printer behavior for type-position syntax. It covers arrays, slices, tuples, paths and qualified paths, references, raw pointers, bare function types, `impl Trait`, trait objects, inferred and never types, macros in type position, invisible groups, and verbatim fallback tokens.

Important APIs/types/functions: exports the non-exhaustive `Type` enum and structs `TypeArray`, `TypeBareFn`, `TypeGroup`, `TypeImplTrait`, `TypeInfer`, `TypeMacro`, `TypeNever`, `TypeParen`, `TypePath`, `TypePtr`, `TypeReference`, `TypeSlice`, `TypeTraitObject`, `TypeTuple`, `Abi`, `BareFnArg`, `BareVariadic`, and `ReturnType`. Parsing entry points include `Parse for Type`, `Type::without_plus`, `ambig_ty`, `ReturnType::without_plus`, `TypeTraitObject::without_plus`, and `TypeImplTrait::without_plus`. Printing is through `quote::ToTokens` implementations for each type node.

Control flow: `ambig_ty` drives ambiguous type parsing. It first handles transparent groups and group-qualified paths, then optional `for<...>` lifetimes, parenthesized forms, function-pointer syntax, paths and type macros, `dyn` trait objects, array/slice brackets, raw pointers, references, never type, `impl Trait`, `_`, and lifetime-started trait objects. Special paths convert into trait objects when `for` lifetimes or `+` bounds are present. Parenthesized syntax distinguishes unit tuple, one-element tuple, parenthesized type, and parenthesized trait-bound object. Bare function parsing separates regular inputs from variadics and preserves unsupported `self` spellings as verbatim.

State and persistence: no persistent runtime state. AST nodes retain token spans and delimiters for later diagnostics and printing. Parser state is limited to `ParseStream` forks and cursors; printer state is only the output `TokenStream`.

Dependencies and integration: integrates with Syn modules for attributes, expressions, generics, lifetimes, macros, paths, punctuation, tokens, verbatim extraction, groups, and errors. Feature gates split parsing and printing. Downstream procedural macros consume these AST types and must account for `Type` being non-exhaustive.

Risks: ambiguity handling around `+`, parenthesized trait bounds, transparent groups, and qualified paths is subtle and can change parse shape. `TypeTraitObject` and `TypeImplTrait` enforce at least one trait-like bound, so lifetime-only input becomes an error. `TypePtr` and `TypeReference` intentionally call `without_plus`, which affects casts and precedence. Unsupported grammar is preserved as `Type::Verbatim`, which can defer errors to later consumers.

Test signals: parser round trips for Rust type grammar, quote/to-token tests, Syn feature-matrix tests for `parsing` and `printing`, and downstream procedural macro tests that match all currently known `Type` variants.
