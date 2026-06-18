# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/dashboard_test.go

Purpose: tests dashboard password generation, password Secret persistence, dashboard Service/module behavior, and self-signed certificate retry handling.

Important APIs and tests: `TestGeneratePassword` validates requested password lengths. `TestGetOrGeneratePassword` verifies missing Secret creation, owner-backed storage, decode, and reuse. `TestStartSecureDashboard` mocks Ceph commands, drives `configureDashboardService` and `configureDashboardModules`, checks module enable/disable counts, retry count, service port/targetPort behavior, and service deletion. `TestCreateSelfSignedCertRetriesWrappedDeadlineExceeded` validates retry behavior when cert creation returns wrapped `context.DeadlineExceeded`.

Control flow: the secure dashboard test sets dashboard wait time to zero, uses a mock executor to simulate module readiness failures via `EINVAL`, and toggles dashboard enabled/disabled plus port values. It checks that public port 443 maps to internal 8443, port 1025 maps directly, and port 0 defaults to 8443 under SSL.

State and persistence behavior: fake Kubernetes clientset stores the dashboard password Secret and dashboard Service. Mocked Ceph commands represent Ceph module and dashboard state; no real Ceph state is changed.

Dependencies and integration points: uses Rook test clientsets, fake Ceph executor, `cephclient.ClusterInfo`, Rook Ceph API types, Kubernetes API errors, and `testify`.

Risks: tests assert command counts rather than full argument sequences for all dashboard commands, so some command argument regressions could slip. The global `dashboardInitWaitTime` is mutated and not restored in the visible test, which can affect same-package tests if order-dependent.

Test signals: good coverage for dashboard lifecycle basics, port mapping, password persistence, and retry semantics; limited coverage for mon-store setting keys and per-daemon config cleanup.
