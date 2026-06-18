<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/restartmanager/restartmanager.go -->
# sources/cloud-native/moby/daemon/internal/restartmanager/restartmanager.go

Purpose: decides if and when a container should restart according to Docker restart policies, with exponential backoff and cancellation.

Important APIs and types: `RestartManager`, `ErrRestartCanceled`, constants for backoff timing, `New`, `SetPolicy`, `ShouldRestart`, and `Cancel`.

Control flow: `ShouldRestart` rejects none policy, canceled managers, and concurrent active restarts. It resets backoff after executions of at least 10 seconds, otherwise doubles timeout up to one minute. It evaluates always, unless-stopped, and on-failure/max-retry policies. When restart is needed, it increments restart count, marks active, starts a goroutine that waits for either cancellation or timeout, closes the returned channel, and clears active after timeout. `Cancel` closes the cancel channel once.

State and persistence: in-memory policy, restart count, timeout, active/canceled flags, and cancel channel protected by mutex/once. Restart count may be initialized from persisted container metadata by caller.

Dependencies and integration: used by daemon container supervision after exits.

Risks: caller must wait for the returned channel before acting; calling `ShouldRestart` while active is an error. Backoff and restart count are not persisted here. Cancel sends `ErrRestartCanceled` on the channel and closes it.

Test signals: `restartmanager_test.go` covers initial timeout and timeout reset after long execution; policy matrix is tested elsewhere if at all.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/restartmanager/restartmanager.go -->
