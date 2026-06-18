# sources/cloud-native/buildkit/sourcepolicy/formatter.go

## Purpose
Caches selector-specific compiled matchers and formats converted destination identifiers using exact, regex, or wildcard capture semantics.

## Important APIs, Types, And Functions
- `selectorCache` embeds `*spb.Selector` and lazily caches regex and wildcard compilers.
- `newSelectorCache` initializes `sync.OnceValues` closures.
- `(*selectorCache).Format` applies format rules.
- `wildcardCache` caches wildcard matches by input ref.
- `(*wildcardCache).Match` is mutex-protected.

## Control Flow
Exact format returns the target string. Regex format compiles the selector regex once and uses `ReplaceAllString`. Wildcard format compiles the wildcard once, matches the current ref, and formats placeholders from captured groups; if the ref no longer matches, it returns the original match string.

## State And Persistence
In-memory compiled regex/wildcard and per-ref wildcard match cache only.

## Dependencies And Integration Points
Used by `mutate` for convert rules and by `match` for wildcard/regex selector behavior. Depends on BuildKit wildcard utility and protobuf enum values.

## Risks And Edge Cases
Regex replacement uses Go regexp replacement syntax, so policy authors must use supported placeholder syntax. Returning the original match when wildcard formatting does not match can hide unexpected non-matches if callers do not already ensure matching.

## Test Signals
Engine tests cover regex and wildcard conversion formatting; matcher tests cover matching behavior.
