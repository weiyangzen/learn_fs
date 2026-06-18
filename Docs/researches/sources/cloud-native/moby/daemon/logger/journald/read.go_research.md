# sources/cloud-native/moby/daemon/logger/journald/read.go

Purpose: optional Linux+cgo journald log reader implementing `logger.LogReader` over libsystemd.

Important APIs/types/functions: `reader` holds driver, journal, watcher, config, max ordinal, readiness, and drain deadline. Helpers recover message line, priority/source, attrs, initial seek positions, waiting, draining, and close synchronization. `ReadLogs` starts a goroutine and waits until the reader is positioned.

Control flow/state/persistence: the goroutine locks its OS thread, opens journal or test directory, initializes inotify for follow, removes data-size threshold, filters by full container ID, seeks by tail/since/until, and drains entries into `LogWatcher.Msg`. It tracks `CONTAINER_LOG_EPOCH` and `CONTAINER_LOG_ORDINAL` to know whether writes from this driver instance have reached the journal. `waitUntilFlushedImpl` searches for the last ordinal after close within `readSyncTimeout`.

Dependencies/integration: relies on `sdjournal`, `logger.LogWatcher`, journald field constants from `journald.go`, and backend attrs. It is wired by setting package variable `waitUntilFlushed` in `init`.

Risks: journald seek APIs have race-prone conceptual positions, so tail and follow logic is delicate. Wall-clock timestamps are not monotonic. If journald rate-limits or drops entries, close draining can time out. Build tags mean behavior exists only on supported builds.

Test signals: `read_test.go` and `loggertest.Reader` validate tail/follow/since/until using fake journal files.
