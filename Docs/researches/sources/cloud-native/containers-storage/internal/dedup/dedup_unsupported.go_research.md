<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup_unsupported.go -->
# sources/cloud-native/containers-storage/internal/dedup/dedup_unsupported.go

## Purpose
This non-Linux fallback marks deduplication primitives as unsupported.

## Important APIs, Types, And Functions
`newDedupFiles`, `isFirstVisitOf`, `dedup`, and `readAllFile` all return `errNotSupported`.

## Control Flow
All operations fail immediately with the shared unsupported sentinel.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
`DedupDirs` treats `errNotSupported` as a benign result, so drivers can expose `Dedup` portably.

## Risks And Test Signals
Callers receive zero savings without an error at the orchestration level. Platform-specific tests should ensure unsupported behavior remains non-fatal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup_unsupported.go -->
