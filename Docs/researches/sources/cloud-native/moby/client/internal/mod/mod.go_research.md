# sources/cloud-native/moby/client/internal/mod/mod.go

## Purpose
`mod.go` extracts a display-friendly module version from Go build info without importing `golang.org/x/mod`.

## Important APIs, Types, And Functions
Types: none. Functions: `Version`, `moduleVersion`, `getVersion`, `normalize`, `splitMetadata`, `splitPseudo`, `isTimestamp`, `parseSemVer`.

## Control Flow
`Version` reads build info once, searches main and dependency modules, prefers replacement versions when present, drops devel/empty values, strips selected metadata, and normalizes pseudo-versions by preserving base version and truncating revisions.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `fmt`, `runtime/debug`, `strconv`, `strings`, `sync`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Pseudo-version parsing intentionally implements only recognized Go forms; unrecognized semver variants fall back to the original base. This is for display, not ordering.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
