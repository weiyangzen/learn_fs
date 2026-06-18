# sources/cloud-native/buildkit/sourcepolicy/engine.go

## Purpose
Implements BuildKit's source policy evaluator, allowing policies to allow, deny, or convert source operations before normal source resolution.

## Important APIs, Types, And Functions
- Errors `ErrSourceDenied` and `ErrTooManyOps`.
- `Engine` stores policies and a selector cache map.
- `NewEngine`, `selectorCache`, `Evaluate`, `evaluatePolicies`, and `evaluatePolicy`.

## Control Flow
`Evaluate` returns immediately for no policies or nil ops. Otherwise it repeatedly evaluates policies, because convert rules mutate the source and may trigger more rules. It stops when no mutation occurs or errors after more than 20 iterations. `evaluatePolicy` walks rules in order, matches selectors and constraints, tracks allow/deny with last matching allow/deny winning, short-circuits on conversion mutation, and returns `ErrSourceDenied` if the final deny flag is set.

## State And Persistence
State is in-memory only. Selector regex/wildcard compilation is cached in `sources` behind `sourcesMu`. Source ops are mutated in place.

## Dependencies And Integration Points
Uses solver `pb.SourceOp`, sourcepolicy protobuf types, matcher/mutator helpers, BuildKit logging, pkg/errors, and logrus fields.

## Risks And Edge Cases
Selector cache keys ignore attr constraints, as noted by TODO; this is safe for compiled identifier patterns but not a place to cache constraint regexes. Convert loops rely on the fixed 20-iteration limit. If a mutation occurs and a later evaluation denies, callers receive both `mutated=true` and an error.

## Test Signals
`engine_test.go` covers deny all, allow/deny order, conversion chains, exact/regex/wildcard conversion, HTTP attr conversion, loops, multiple policies, and last-rule-wins behavior.
