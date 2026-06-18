<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/errcode.go -->
# sources/cloud-native/containerd/core/remotes/docker/errcode.go

Purpose: Docker registry error-code model and JSON error envelope handling.

Important APIs/types/functions: `ErrorCoder`, `ErrorCode`, `Error`, `ErrorDescriptor`, `ParseErrorCode`, `Errors`, `unexpectedResponseErr`, plus methods for text marshal/unmarshal, message/detail/args construction, JSON marshal/unmarshal, and error formatting.

Control flow: `ErrorCode` resolves descriptors through generated maps and falls back to `ErrorCodeUnknown`. `Errors.MarshalJSON` normalizes `ErrorCode`, `Error`, and arbitrary errors into an `{"errors":[...]}` envelope. `Errors.UnmarshalJSON` collapses detail-less/default-message entries back to bare `ErrorCode`. `unexpectedResponseErr` wraps remotes unexpected status and, when the response body contains registry errors, joins the status error with typed registry errors.

State and persistence: no persistent state; serialization/deserialization of registry error payloads.

Dependencies and integration points: used by Docker resolver/pusher error paths to expose typed registry errors while retaining HTTP status context. Depends on generated descriptor maps in companion files and `core/remotes/errors`.

Risks: unknown error details may be marshaled as `ErrorCodeUnknown` with arbitrary detail values. `unexpectedResponseErr` type-asserts the unexpected status shape and ignores malformed registry error bodies. Joined errors require callers to use `errors.As/Is` correctly.

Test signals: no direct tests in this subset. Behavior is likely covered by resolver/pusher tests outside this work item.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/errcode.go -->
