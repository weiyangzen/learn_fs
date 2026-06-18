# sources/cloud-native/moby/daemon/names/names.go

## Purpose
This small package defines the shared restricted-name pattern for container and volume names.

## Important APIs, Types, And Functions
`RestrictedNameChars` is the regex fragment `[a-zA-Z0-9][a-zA-Z0-9_.-]`. `RestrictedNamePattern` lazily compiles `^` + fragment + `+$`.

## Control Flow
Consumers call `RestrictedNamePattern.MatchString` to validate names. Lazy compilation defers regex construction until first use.

## State, Persistence, And Dependencies
The only state is the lazy compiled regex. Dependency is Docker's internal `lazyregexp`.

## Integration Points
`daemon/names.go` imports this package for container name validation, and comments indicate volume naming also uses the same rules.

## Risks And Edge Cases
The fragment plus trailing `+` means at least one initial alphanumeric char and zero or more allowed continuation chars. Names must be trimmed of any leading slash by callers before matching.

## Test Signals
No direct tests in this item; validation is exercised by name reservation/create tests elsewhere.
