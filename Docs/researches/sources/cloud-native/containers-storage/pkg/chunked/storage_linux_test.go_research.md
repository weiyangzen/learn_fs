## sources/cloud-native/containers-storage/pkg/chunked/storage_linux_test.go

Purpose: tests selected utility behavior from the Linux chunked storage implementation.

Important APIs/types/functions: `mockImageSource`, `mockReadCloser`, `TestGetBlobAtNormalOperation`, `TestGetBlobAtMaxStreams`, `TestGetBlobAtWithErrors`, `TestGetBlobAtMixedStreamsAndErrors`, and `TestTypeToOsMode`.

Control flow: mock image sources return preloaded stream and error channels. Tests consume the normalized `getBlobAt` channel, verify stream contents, over-return detection, error forwarding, mixed stream/error handling, stream close behavior, and tar type to `os.FileMode` conversion.

State and persistence: in-memory channels/readers only; no filesystem mutations.

Dependencies and integration points: validates helper behavior used by `copyAllBlobToFile` and missing-chunk fetch paths. Uses `testify`.

Risks: does not test real range requests, `ErrBadRequest` retry/merge behavior, partial extraction, cache dedupe, or graph-driver integration.

Test signals: good channel-draining regression coverage. Local execution unavailable because the Go toolchain is missing.
