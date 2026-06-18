# sources/cloud-native/cri-o/internal/watchdog/suite_test.go

Purpose: Ginkgo suite bootstrap for systemd watchdog tests.

Important APIs/types/functions: `TestWatchdog`, package-level framework `t`, `BeforeSuite`, and `AfterSuite`.

Control flow: registers fail handler, runs specs named `Watchdog`, and manages shared framework setup/teardown.

State and persistence: no durable state; framework state only.

Dependencies/integration: CRI-O test framework plus Ginkgo/Gomega.

Risks: tests rely on build tag support for the injection file to set mock systemd.

Test signals: enables the mock-based watchdog test file.
