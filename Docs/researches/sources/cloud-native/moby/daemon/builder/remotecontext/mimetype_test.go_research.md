# sources/cloud-native/moby/daemon/builder/remotecontext/mimetype_test.go

## Purpose
Provides a minimal unit test that `detectContentType` recognizes a plain text byte slice and returns the normalized `text/plain` constant.

## Important APIs, Types, And Functions
Tests `detectContentType` and `mimeTypeTextPlain` using `gotest.tools` assertions.

## Control Flow
The test sends a simple ASCII sentence to `detectContentType`, asserts no error, and checks the exact returned media type.

## State And Persistence
No state or filesystem access.

## Dependencies And Integration Points
Directly guards the helper used by remote context response inspection.

## Risks And Test Signals
Coverage is narrow: it does not test charset stripping, binary data, or parse errors. A failure indicates drift in MIME sniffing assumptions or constant values.
