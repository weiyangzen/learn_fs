<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/generics.rs -->
# sources/distributed-fs/ceph-client/rust/syn/generics.rs

## Purpose

`generics.rs` defines Syn's AST representation, parsing, helper APIs, and printing behavior for Rust generic parameters and where clauses. It covers declaration-site generics such as lifetimes, type parameters, const parameters, bounds, higher-ranked lifetimes, precise capture bounds, and where predicates. It also provides ergonomic helpers used by procedural macros when generating impl blocks from parsed types.

The file is central to item, trait, impl, function, type, and path-related AST handling. It owns both the stable data model, such as `Generics`, `GenericParam`, `TypeParam`, and `WhereClause`, and grammar-sensitive logic such as parsing `<T>` generic parameter lists versus qualified paths.

## Important APIs, Types, and Functions

- `Generics` stores optional `<` and `>` tokens, a `Punctuated<GenericParam, Comma>` parameter list, and an optional `WhereClause`.
- `GenericParam` distinguishes `Lifetime`, `Type`, and `Const` parameters.
- `LifetimeParam`, `TypeParam`, and `ConstParam` store attributes, names, bounds, type/default expressions, and syntax tokens for each parameter kind.
- `Generics::lifetimes`, `type_params`, `const_params` and their `_mut` variants filter `params` by variant using iterator wrappers.
- `Generics::make_where_clause` lazily inserts an empty `where` clause and returns it for mutation.
- `Generics::split_for_impl` returns `ImplGenerics`, `TypeGenerics`, and `Option<&WhereClause>` for quote-friendly impl generation.
- `BoundLifetimes` represents `for<'a, ...>` binders.
- `TypeParamBound` supports trait bounds, lifetime bounds, full-only precise capture bounds (`use<...>`), and verbatim fallback tokens.
- `TraitBound` and `TraitBoundModifier` represent trait paths, optional higher-ranked binders, optional parentheses, and `?` polarity.
- `PreciseCapture` and `CapturedParam` model the full-only `impl Trait + use<'a, T>` syntax.
- `WhereClause`, `WherePredicate`, `PredicateLifetime`, and `PredicateType` model `where` constraints.

Parsing and printing modules are feature-gated. Parsing implements `Parse` for the generic AST nodes, while printing implements `ToTokens` for nodes and wrapper types.

## Control Flow

Parsing `Generics` starts by checking for `<`; if absent it returns `Generics::default()`. If present, it parses a comma-separated list of parameters until `>`, preserving attributes per parameter and dispatching by lookahead to lifetime, identifier/type, `const`, or underscore type parameter handling.

Parameter parsing is variant-specific. `LifetimeParam` optionally parses a colon and lifetime bounds. `TypeParam` parses an identifier, optional bounds after `:`, and an optional type default after `=`. `ConstParam` parses `const IDENT: Type` and optional default expression using `path::parsing::const_argument`.

Bound parsing handles several grammar edge cases. `TypeParamBound::parse_single` accepts lifetimes first, then full-only precise capture syntax, then optional parentheses around a `TraitBound`, and falls back to `Verbatim` if a trait bound cannot be parsed. `TraitBound::do_parse` handles `for<...>`, optional `[const]` or `const` in allowed contexts, `?Sized`, and parenthesized generic arguments such as `Fn(A) -> B`.

`WhereClause` parsing stops on common item delimiters such as braces, semicolons, top-level commas, colons, and equals signs. `WherePredicate` chooses lifetime predicates when it sees `Lifetime :`; otherwise it parses a type predicate with optional `for<...>`.

Printing separates declaration generics, impl generics, type generics, and turbofish output. Lifetimes are emitted before type and const parameters regardless of stored order. `ImplGenerics` omits defaults but keeps bounds. `TypeGenerics` emits only parameter identifiers/lifetimes and omits bounds/defaults. `Turbofish` prefixes type generics with `::`. `print_const_argument` emits simple const arguments directly and wraps complex expressions in braces to preserve valid Rust syntax.

## State and Persistence Behavior

The file has no global mutable state. Persistent state is the AST stored in public structs and enums. Token fields preserve source spans and syntax shape for round-tripping. `make_where_clause` is the primary mutating helper; it inserts a default `where` token and empty predicate list only when absent.

Iterator helpers expose borrowed or mutable borrowed views into the single `params` list. They do not copy or reorder parameters. Printing may reorder lifetimes before other parameters in emitted tokens, but it does not mutate the stored AST.

The parsing module may store unrecognized or currently unsupported bound syntax as `TypeParamBound::Verbatim`, preserving tokens for later printing or downstream handling rather than rejecting every future grammar form.

## Dependencies and Integration Points

This module depends on Syn AST modules for attributes, expressions, identifiers, lifetimes, paths, punctuated lists, tokens, and types. Parsing depends on `Parse`, `ParseStream`, lookahead, `IdentExt`, error construction, parenthesized/bracketed parsing macros, and `verbatim::between`. Printing depends on `quote::ToTokens`, `TokenStreamExt`, `TokensOrDefault`, attribute filtering, and full-mode expression fixup.

Integration points are broad: item parsing uses `Generics` for structs, enums, traits, impls, functions, type aliases, and associated items; path and type parsing use bounds and bound lifetimes; code generation commonly uses `split_for_impl`; `visit_mut.rs` traverses all these types; and quote-based output depends on wrapper printing semantics.

## Risks and Edge Cases

- The `choose_generics_over_qpath` heuristic is syntax-sensitive. Regressions can misparse ambiguous constructs such as `impl <T>::Assoc` versus `impl<T> Type`.
- Printing lifetimes before type and const parameters is intentional for valid Rust output but can surprise consumers expecting exact original order.
- `ImplGenerics` and `TypeGenerics` intentionally omit defaults in different ways. Including defaults in impl headers or type use sites would generate invalid Rust.
- Precise capture (`use<...>`) is full-only and forbidden in some bound contexts. The parser returns targeted errors when syntax appears where not allowed.
- `TraitBound::do_parse` returns `Ok(None)` for allowed const-bound prefixes because this syntax is recognized but not represented as a normal trait bound here; callers must handle that contract.
- Const generic defaults require expression parsing and printing fixups. Complex expressions must be braced during printing to avoid invalid token output.

## Test Signals

Strong tests include Syn parser tests for generic declarations, where clauses, higher-ranked trait bounds, const generics, default generic parameters, qualified path ambiguities, precise capture syntax, and trait object bounds. Quote round-trip tests should verify `split_for_impl`, `as_turbofish`, omitted defaults, lifetime ordering, and braced const argument output. Feature matrix tests with `full`, `derive`, `parsing`, `printing`, `clone-impls`, and `extra-traits` catch most cfg-specific regressions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/generics.rs -->
