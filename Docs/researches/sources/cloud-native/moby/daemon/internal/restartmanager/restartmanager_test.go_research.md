<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/restartmanager/restartmanager_test.go -->
# sources/cloud-native/moby/daemon/internal/restartmanager/restartmanager_test.go

Purpose: verifies restart backoff initialization and reset behavior.

Important APIs and types: `TestRestartManagerTimeout` and `TestRestartManagerTimeoutReset`.

Control flow: tests create an always policy manager, call `ShouldRestart`, and inspect `rm.timeout`. The reset test preloads a five-second timeout and uses a ten-second execution duration to confirm reset to default.

State and persistence: directly inspects in-memory manager fields.

Dependencies and integration: uses Docker container restart policy type.

Risks: tests do not wait on the returned restart channel, so active goroutines may briefly remain. They do not cover cancellation, on-failure, unless-stopped, max retry, or active-call errors.

Test signals: narrow but useful coverage of backoff timing contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/restartmanager/restartmanager_test.go -->
