# sources/cloud-native/moby/pkg/process/process_unix.go

Purpose: Unix implementation for process liveness, killing, and exported zombie checks.

APIs and flow: `alive` uses `unix.Kill(pid, 0)` on Darwin and treats `EPERM` as alive; other Unix systems check for `/proc/<pid>`. `kill` sends `SIGKILL` and ignores `ESRCH`. `Zombie` delegates to the platform `zombie` helper.

State and dependencies: relies on procfs or kernel signal APIs, with no durable state.

Integration points: shared by all non-Windows builds; Linux gets zombie parsing from `process_linux.go`.

Risks and tests: procfs presence assumptions affect non-Darwin Unix ports. `Kill` swallowing `ESRCH` makes it idempotent for already-gone processes.
