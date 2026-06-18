# sources/control-plane/rook/tests/integration/ceph_base_deploy_test.go

Common deployment bootstrap and health helpers for Rook Ceph integration suites. It defines `defaultNamespace`, the shared package `logger`, cluster install/health checks, ingress check, panic cleanup, and `StartTestCluster`.

`StartTestCluster` creates a `K8sHelper`, records Kubernetes version in settings, sets global DEBUG logging, creates a `CephInstaller`, installs Rook, gathers logs and uninstalls on failure, then returns installer/helper handles. `checkIfRookClusterIsInstalled` asserts operator, mgr, osd, mon, and crashcollector pod counts/states. `checkIfRookClusterIsHealthy` polls `clients.IsClusterHealthy`, and `HandlePanics` runs suite teardown before failing the test on panic.

State is mostly delegated to `CephInstaller`, but this file mutates test settings, global logging, and can uninstall live cluster resources through panic handling. Dependencies are `utils`, `installer`, `clients`, capnslog, and testify suite assertions.

Risks: exact pod counts/labels can be brittle during upgrades or multi-manager setups; the health helper can give limited diagnostics when health remains false; global log-level changes affect all tests. Test signals are install return values, pod count/state checks, Ceph health, ingress status, and collected logs on install failure.
