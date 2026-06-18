# sources/cloud-native/moby/client/pkg/versions/compare.go

## Purpose
`compare.go` compares dotted API/version strings numerically segment-by-segment.

## Important APIs, Types, And Functions
Types: none. Functions: `compare`, `LessThan`, `LessThanOrEqualTo`, `GreaterThan`, `GreaterThanOrEqualTo`, `Equal`.

## Control Flow
`compare` splits version strings on dots, parses numeric components, and exposes boolean helpers for less-than/equal/greater-than comparisons.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `strconv`, `strings`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Non-numeric segments parse as zero-like failures depending on `strconv.Atoi`; this helper is suited to Docker API version strings, not general semantic versioning.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
