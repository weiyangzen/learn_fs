# sources/cloud-native/moby/daemon/server/httputils/form.go

## Purpose
Provides request form/query parsing helpers for Docker API handlers, including booleans, integers, repository tags, archive parameters, and OCI platform JSON.

## Important APIs, Types, And Functions
Functions include `BoolValue`, `BoolValueOrDefault`, `Uint32Value`, `Int64ValueOrZero`, `Int64ValueOrDefault`, `RepoTagReference`, `ArchiveFormValues`, `DecodePlatform`, and `DecodePlatforms`. `ArchiveOptions` carries container archive name/path.

## Control Flow
Boolean parsing treats empty, `0`, `no`, `false`, and `none` as false and anything else as true. `Uint32Value` manually strips a negative sign to distinguish syntax and range errors. Repo/tag parsing normalizes names, rejects digest references, and defaults missing tags to `latest`. Platform decoding requires OS and architecture when any platform is specified and rejects optional-only payloads.

## State And Persistence
Helpers only read request form state and return values; `ArchiveFormValues` calls `ParseForm`, which may populate `r.Form`.

## Dependencies And Integration Points
Used throughout container/image/archive routes. Depends on distribution reference parsing, daemon errdefs, and OCI platform specs.

## Risks And Edge Cases
Loose boolean parsing makes arbitrary non-false strings true. `Int64ValueOrZero` suppresses parse errors, while `Int64ValueOrDefault` surfaces them. Platform JSON must be a full JSON object, not Docker platform shorthand.

## Test Signals
`form_test.go` covers boolean cases, int parsing, uint32 syntax/range behavior, and detailed platform validation.
