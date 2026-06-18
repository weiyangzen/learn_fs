<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/readers_test.go -->
# sources/cloud-native/moby/pkg/ioutils/readers_test.go

Purpose: unit tests for read closer wrappers. Tests verify the custom closer runs only once and that `NewCancelReadCloser` stops a perpetual reader when context is canceled or closed. State is in-memory readers and contexts. Dependencies include `io`, context cancellation, and timeouts. Risks covered include double close and stuck reads; tests may be timing-sensitive around cancellation. Test signal is focused on wrapper lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/ioutils/readers_test.go -->
