# sources/cloud-native/moby/client/pkg/progress/progressreader.go

## Purpose
`progressreader.go` wraps an `io.ReadCloser` and emits progress updates as bytes are read or when closed early.

## Important APIs, Types, And Functions
Types: `Reader`. Functions: `NewProgressReader`, `Read`, `Close`, `updateProgress`.

## Control Flow
`Read` increments the current byte count and emits updates; `Close` emits a final update when the stream ended early, then closes the underlying reader.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `io`, `time`, `golang.org/x/time/rate`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Premature close semantics matter for upload progress; double-close and final-update behavior must stay stable.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
