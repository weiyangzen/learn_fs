# sources/cloud-native/cri-o/internal/watchdog/watchdog_test.go

Purpose: validates watchdog control flow with a mocked systemd backend and in-memory health checkers.

Important APIs/types/functions: uses `watchdog.New`, test-only `SetSystemd`, `Start`, and `Notifications`; defines `waitForNotifications` polling helper.

Control flow: each spec sets gomock expectations for `WatchdogEnabled`/`Notify`, starts the watchdog, waits until notification attempts or health-check flags indicate the goroutine ran, and asserts errors/side effects.

State and persistence: only in-memory booleans and atomic notification counts. No real systemd socket or durable state is used.

Dependencies/integration: requires the `test` build-tag injection file and generated `systemd` mock.

Risks: asynchronous polling can hang if expected notifications never arrive; gomock expectations and Ginkgo timeouts bound this indirectly. The "does not acknowledge" test proves no startup error, but the actual failure is logged asynchronously.

Test signals: confirms health-check short-circuiting, retry count behavior, disabled watchdog no-op, and invalid interval rejection.
