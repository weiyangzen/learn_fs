# sources/distributed-fs/ceph-client/rust/syn/classify.rs

## Purpose

This file classifies Syn expression and type shapes for correct parsing/printing decisions around semicolons, match-arm commas, trailing braces, labels, and ambiguous type paths.

## Important APIs, types, and functions

`requires_semi_to_be_stmt` and `requires_comma_to_be_match_arm` classify expression statement and match arm punctuation. `trailing_unparameterized_path` walks types to determine whether a printed type ends in an unparameterized path. `expr_leading_label` detects whether an expression's first token is a loop/block label. `expr_trailing_brace` determines whether an expression's last token is `}`, recursing into nested expressions and relevant type positions.

## Control flow

The functions are pattern-match walkers over Syn AST enums. They either return immediately for known terminal variants or follow left/right/base/body/type fields until a terminal shape is reached. Helper functions inspect last path segments, parenthesized return types, trait bounds, and verbatim token streams.

## State and persistence behavior

No state is mutated. The module computes boolean classification from immutable AST references.

## Dependencies and integration points

It depends on `Expr` and, under printing/full features, `Type`, `Path`, `PathArguments`, `ReturnType`, `TypeParamBound`, `Punctuated`, `ControlFlow`, and token-stream group inspection. Syn printers use these classifications to decide punctuation and disambiguation.

## Risks and test signals

Risks include missing new `Expr` or `Type` variants, wrong punctuation around macros and brace-delimited expressions, incorrect handling of labels through nested receiver/left expressions, and generic path ambiguity. Tests should cover every expression variant, macro delimiters, chained field/call/index/cast forms, function/trait-object return types, verbatim brace tokens, and compiler parse/pretty-print round trips.
