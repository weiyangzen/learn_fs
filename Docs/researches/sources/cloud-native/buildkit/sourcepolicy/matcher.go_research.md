# sources/cloud-native/buildkit/sourcepolicy/matcher.go

## Purpose
Determines whether a source operation matches a policy selector and its attribute constraints.

## Important APIs, Types, And Functions
- `match(src, ref, constraints, attrs)` returns a boolean match or error.

## Control Flow
The function first validates all attr constraints: equality, inequality, and regex matching against the op attrs. Any failed constraint returns false. Then it checks direct identifier equality, exact mode, regex mode via cached selector regex, wildcard mode via cached wildcard matcher, or errors on unknown match type.

## State And Persistence
No persistence. Regex constraints are compiled per call; selector identifier regex/wildcard compilers are cached in `selectorCache`.

## Dependencies And Integration Points
Used by `Engine.evaluatePolicy`. Depends on `regexp`, sourcepolicy protobufs, and pkg/errors.

## Risks And Edge Cases
Nil constraints and unknown enum values are errors. Missing attrs behave as empty string, so `NOTEQUAL` constraints can match missing keys when the value is non-empty. Constraint regexes are not cached despite the engine TODO.

## Test Signals
`matcher_test.go` covers exact, wildcard, scheme-sensitive matches, attr equality/inequality/regex constraints, missing attrs, multiple constraints, and invalid condition errors.
