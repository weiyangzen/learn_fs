# sources/cloud-native/moby/client/pkg/jsonmessage/jsonmessage.go

## Purpose
`jsonmessage.go` renders daemon JSON progress messages to terminals or plain streams, including progress bars, aux callbacks, line clearing, and compatibility wrappers.

## Important APIs, Types, And Functions
Types: `DisplayOpt`, `displayOpts`, `JSONMessagesStream`. Functions: `WithAuxCallback`, `RenderTUIProgress`, `clearLine`, `cursorUp`, `cursorDown`, `Display`, `DisplayJSONMessagesStream`, `DisplayStream`, `displayJSONMessagesStream`, `DisplayJSONMessages`, `DisplayMessages`, `displayJSONMessages`.

## Control Flow
Display functions decode messages or consume iterators, route aux messages to callbacks, render status/progress/error records, and use terminal cursor movement only when terminal mode is enabled.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `encoding/json`, `errors`, `fmt`, `io`, `iter`, `strings`, `time`, `github.com/docker/go-units`, `github.com/moby/moby/api/types/jsonstream`, `github.com/moby/term`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Terminal control sequences and progress width calculations are easy to regress. Error messages embedded in JSON stream records must stop display with useful errors.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
