<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/ops.go -->
# sources/cloud-native/moby/internal/testutil/request/ops.go

Purpose: functional options for constructing raw HTTP requests to the daemon in tests. Important APIs include `Options`, `Host`, `With`, `Method`, `RawString`, `RawContent`, `ContentType`, `JSON`, and `JSONBody`. Control flow accumulates request mutators that later set method, body, and headers; `JSONBody` encodes arbitrary data into a buffer and marks content type. State is the mutable options struct and request body readers. Dependencies are standard HTTP, JSON, and IO packages. Risks include body readers being single-use, errors from JSON encoding surfacing during request construction, and option ordering. Test signal is indirect through API integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/ops.go -->
