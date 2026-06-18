# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/provider/stream_content_test.go

Purpose: focused unit tests for the standalone StreamContent implementation.

Important APIs under test: `Writer`, `ReaderAt`, `SetDefaultRef`, `Info`, `Update`, `Delete`, `Status`, `ListStatuses`, `Abort`, `copyMap`, `isFetchRef`, `hasPrefix`, `newMemWriter`, `memWriter.Truncate`, `memWriter.Commit`, and `bytesReaderAt`.

Control flow and state: tests write generated payloads through the memory writer, commit them, and read them back by digest. Fetch refs are expected to return `ErrAlreadyExists` with no writer. Info/update/delete tests prove label maps are copied on read/update and cleared by delete. Helper tests verify prefix classification.

Dependencies and integration points: uses containerd writer options and errors, OCI descriptors, and digest helpers, but avoids network fetch by reading from in-memory blobs.

Risks and test signals: tests explicitly assert that truncating after a digest was computed keeps the original digest value, which is a surprising behavior for callers expecting digest to track truncated content. The remote fetch branch with a populated default ref is not exercised here.
