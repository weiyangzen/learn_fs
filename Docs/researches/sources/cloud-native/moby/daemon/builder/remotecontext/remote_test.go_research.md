# sources/cloud-native/moby/daemon/builder/remotecontext/remote_test.go

## Purpose
Tests remote-context response inspection, MIME selection, HTTP download behavior, and status-code error handling.

## Important APIs, Types, And Functions
Defines `binaryContext`, tests `selectAcceptableMIME`, `inspectResponse`, `downloadRemote`, and `GetWithStatusError`, plus helper `readBody`.

## Control Flow
Tests validate accepted tar/compression/text/octet MIME values and rejected JSON/empty/incomplete strings. `inspectResponse` cases cover empty response errors, binary octet-stream preservation, unsupported content type returning a replayable body, text/plain, missing content type sniffed as text, and unknown content length. `TestDownloadRemote` serves a temp Dockerfile through `httptest`. Status tests assert 200 body reads and 400 body-in-error text.

## State And Persistence
Uses temp directories and in-memory test servers. All state is test-scoped.

## Dependencies And Integration Points
Depends on `httptest`, `builder.DefaultDockerfileName`, and `createTestTempFile` from `utils_test.go`. It confirms `remote.go` preserves response bodies for later build processing.

## Risks And Test Signals
The suite does not cover every HTTP error mapping or DNS classification. Failures usually indicate preamble replay corruption, MIME regression, or error wrapping changes visible to API callers.
