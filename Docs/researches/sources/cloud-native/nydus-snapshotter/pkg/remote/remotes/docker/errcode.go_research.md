# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/errcode.go

## Purpose
Defines Docker distribution-style error codes, descriptors, error wrappers, and JSON envelope conversion.

## Important APIs, Types, And Functions
`ErrorCode`, `Error`, `ErrorDescriptor`, `Errors`, `ParseErrorCode`, `WithMessage`, `WithDetail`, `WithArgs`, and JSON marshal/unmarshal methods are the primary API.

## Control Flow
`ErrorCode` resolves metadata through descriptor maps populated in `errdesc.go`. `Errors.MarshalJSON` converts each element into a serializable `Error`, filling default messages. `Errors.UnmarshalJSON` decodes an `errors` array and collapses detail-less default-message entries back to bare `ErrorCode` values.

## State And Persistence
No persistent state here, but it depends on global descriptor registries initialized by `Register` in `errdesc.go`.

## Dependencies And Integration Points
Used by fetcher error handling to decode registry JSON errors and include server messages. The JSON shape matches Docker Registry API error envelopes.

## Risks And Edge Cases
Unknown text unmarshals to `ErrorCodeUnknown`. `Errors` is a slice of `error`, so callers must be prepared for `ErrorCode`, `Error`, or unknown wrapped errors. Error strings are for humans, not stable programmatic IDs.

## Test Signals
No direct tests in this subset, but `fetcher_test.go` verifies registry error envelopes can surface a server message when fetch requests fail.
