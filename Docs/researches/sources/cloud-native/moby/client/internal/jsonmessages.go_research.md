# sources/cloud-native/moby/client/internal/jsonmessages.go

## Purpose
`jsonmessages.go` wraps a daemon JSON-message response body as an `io.ReadCloser`, an iterator of `jsonstream.Message`, and a blocking `Wait` helper.

## Important APIs, Types, And Functions
Types: `Stream`, `httpError`. Functions: `NewJSONMessageStream`, `Read`, `Close`, `JSONMessages`, `Wait`, `Error`, `Unwrap`, `Is`, `httpErrorFromStatusCode`.

## Control Flow
`JSONMessages` registers a context cancellation callback that closes the body, decodes messages until EOF/error, suppresses decode noise when the context is canceled, and always closes once. `Wait` returns the first transport/decode/context error or message-level daemon error mapped through HTTP errdefs.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `errors`, `io`, `iter`, `sync`, `github.com/containerd/errdefs/pkg/errhttp`, `github.com/moby/moby/api/types/jsonstream`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
The nil-reader constructor panics by design. Iterator users must respect context cancellation and message errors; incorrect status-code mapping would break callers checking errdefs.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
