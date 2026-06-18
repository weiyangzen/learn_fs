# sources/cloud-native/moby/daemon/logger/journald/read_test.go

Purpose: end-to-end tests for journald `ReadLogs` under Linux+cgo+journald builds.

Important APIs/types/functions: `TestLogRead` uses `loggertest.Reader` with a factory that creates a journal file via `fake.NewT`, injects `sendToJournal`, `journalReadDir`, and `readSyncTimeout`, then runs tail and follow suites. `syncLogger` calls `waitUntilFlushedImpl`.

Control flow/state/persistence: tests persist entries to a temporary `.journal` file through `systemd-journal-remote`, then reopen logger instances against the same directory to simulate stopped/live containers.

Dependencies/integration: depends on fake sender, sdjournal read path, `loggertest.Reader`, and systemd tools.

Risks: skipped or environment-sensitive if external tools are missing. Timing-sensitive parts use sync flush and test readiness to reduce flakes.

Test signals: strong integration signal for journald readback including follow, tail, since/until, and closed-container draining.
