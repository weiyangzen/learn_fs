# sources/cloud-native/moby/client/pkg/progress/progress.go

## Purpose
`progress.go` defines the small progress event model and output abstraction shared by stream formatters and progress readers.

## Important APIs, Types, And Functions
Types: `Progress`, `Output`, `chanOutput`, `discardOutput`. Functions: `WriteProgress`, `ChanOutput`, `WriteProgress`, `DiscardOutput`, `Update`, `Updatef`, `Message`, `Messagef`, `Aux`.

## Control Flow
Helper functions construct `Progress` values for status, formatted messages, and aux payloads, then send them to an `Output` implementation such as channel output or discard output.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `fmt`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
The abstraction is intentionally tiny; downstream formatters rely on stable field meaning for ID, action, current, total, message, error, and aux.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
