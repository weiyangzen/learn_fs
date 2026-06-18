# sources/cloud-native/moby/client/pkg/streamformatter/streamformatter.go

## Purpose
`streamformatter.go` formats progress events as either human-readable raw text or JSON messages for Docker stream output.

## Important APIs, Types, And Functions
Types: `jsonProgressFormatter`, `rawProgressFormatter`, `formatProgress`, `progressOutput`. Functions: `appendNewline`, `format`, `emptyMessage`, `formatStatus`, `formatProgress`, `format`, `emptyMessage`, `rawProgressString`, `formatProgress`, `NewProgressOutput`, `NewJSONProgressOutput`, `WriteProgress`.

## Control Flow
Formatter implementations convert `progress.Progress` into status lines, progress bars, aux JSON, or newline-delimited JSON. `progressOutput.WriteProgress` serializes access with a mutex before writing to the destination.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `encoding/json`, `fmt`, `io`, `strings`, `sync`, `time`, `github.com/docker/go-units`, `github.com/moby/moby/api/types/jsonstream`, `github.com/moby/moby/client/pkg/progress`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Concurrent writes require locking; raw progress math must avoid divide-by-zero and terminal-width artifacts. JSON output must keep daemon-compatible field names.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
