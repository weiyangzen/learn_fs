# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/inspector.go

Purpose: wraps `nydus-image inspect` for extracting metadata from a Nydus bootstrap, currently blob information.

Important APIs and flow: `InspectOption` contains `Operation` and `Bootstrap`. `BlobInfo` maps JSON fields for blob ID, compressed/decompressed size, and readahead data; `String` methods marshal objects/lists as JSON. `NewInspector` stores the binary path. `(*Inspector).Inspect` builds `nydus-image inspect <bootstrap> --request blobs` for `GetBlobs`, runs `CombinedOutput`, wraps command failures with output text, unmarshals the JSON into `BlobInfoList`, and rejects unsupported operations with `not support method`.

State and persistence: no persistent state. Reads bootstrap via external command and returns decoded in-memory metadata.

Dependencies and integration: used by checker/tooling that needs blob layout from a bootstrap. Depends on external `nydus-image` output schema.

Risks and test signals: command output must be pure JSON on success. Unsupported operations use integer constants, so adding operations requires updating both dispatch and callers.
