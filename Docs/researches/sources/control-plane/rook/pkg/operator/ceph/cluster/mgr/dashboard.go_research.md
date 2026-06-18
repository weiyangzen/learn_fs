# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/dashboard.go

Purpose: manages Ceph mgr dashboard exposure and module configuration, including the Kubernetes Service, Ceph module enable/disable, monitor-store settings, self-signed TLS certificate, dashboard admin password Secret, and login credentials.

Important APIs and functions: `configureDashboardService` creates/updates or deletes the dashboard Service. `configureDashboardModules` enables/disables the Ceph dashboard module and performs initialization/config. `deleteManagerDaemonConfiguration` removes old per-daemon dashboard config keys. `configureDashboardModuleSettings` writes global dashboard settings. `initializeSecureDashboard`, `createSelfSignedCert`, `setLoginCredentials`, `getOrGenerateDashboardPassword`, `GeneratePassword`, `GenerateRandomBytes`, and `decodeSecret` handle secure dashboard setup.

Control flow: if dashboard is disabled, service is deleted and module disable is attempted. If enabled, the module is enabled, initialization waits briefly, a password Secret is fetched or generated, a self-signed cert is created when SSL is enabled, login credentials are applied with retrying Ceph dashboard commands, global settings are written to the mon store, stale per-daemon settings are removed once, and the dashboard module is restarted if cert or config changed.

State and persistence behavior: persists the `rook-ceph-dashboard-password` Secret owned by the cluster, creates/deletes a dashboard Service, writes mon-store config under `mgr/dashboard/*`, creates Ceph dashboard cert/config-key state, and creates/updates dashboard user credentials in Ceph. A package-level `removeMgrDaemonConfiguration` boolean controls one-time cleanup attempts across calls.

Dependencies and integration points: uses Ceph client module/config/dashboard commands, Rook config mon store, Kubernetes Services/Secrets, owner references, random crypto, temp password files, command retry helpers, and dashboard Service construction from `spec.go`.

Risks: dashboard initialization uses sleeps and retries because the module may not be immediately ready. `createSelfSignedCert` returns success with no error after retry exhaustion, which avoids blocking reconcile but can leave SSL not fully initialized. Passwords are written to temp files and removed with deferred cleanup; logging avoids printing the password except secret-sourced values could be exposed by lower-level debug if changed. The package-level per-daemon cleanup flag is shared process-wide, not per cluster.

Test signals: `dashboard_test.go` covers password generation/reuse, service port mapping including privileged public ports, enable/disable module counts, self-signed cert retry on invalid-argument readiness and wrapped deadline exceeded, and service deletion.
