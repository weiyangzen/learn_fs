# sources/control-plane/rook/pkg/daemon/ceph/client/crash_test.go

Purpose: provides a minimal unit test for crash listing.

Important test cases: `TestCephCrash` configures a mock executor that returns a single crash entry for `ceph crash ls`, calls `GetCrashList()`, and asserts no error plus one returned record. The `fakecrash` fixture includes `crash_id`, `timestamp`, `process_name`, and `entity_name`.

Control flow and dependencies: the mock checks `args[0] == "crash"` and `args[1] == "ls"`, relying on `NewCephCommand()` appending standard args after the command-specific arguments. It uses `AdminTestClusterInfo()` and `exectest.MockExecutor`.

Risks and coverage gaps: the test confirms the happy path but does not validate field-level unmarshalling, command errors, invalid JSON, `GetCrash()` delegation, or `ArchiveCrash()`. It also does not cover optional fields such as assertion details, IO error metadata, or backtrace.
