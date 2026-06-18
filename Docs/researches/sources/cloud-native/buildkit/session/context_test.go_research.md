<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/context_test.go -->
# sources/cloud-native/buildkit/session/context_test.go

Purpose: tests cancellation behavior for contexts derived from session caller contexts.

Important APIs, types, and functions: `TestContextWithCaller` has subtests for caller close canceling the derived context with `context.DeadlineExceeded`, and base request close canceling with `context.Canceled`.

Control flow and state: uses `select` with a 5 second timeout to ensure cancellation occurs.

Dependencies and integration: validates the helper used by session callers in `manager.go`.

Risks and test signals: tests do not check cleanup of the registered AfterFunc or simultaneous cancellation ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/context_test.go -->
