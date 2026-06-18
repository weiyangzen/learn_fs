# sources/control-plane/rook/tests/framework/clients/cluster.go

Purpose: this file provides cluster health validation for integration tests. `IsClusterHealthy` verifies high-level Ceph status returned through the shared `TestClient`.

Important APIs/types/functions: `IsClusterHealthy(testClient, namespace)` returns a boolean and detailed error. Helper `monInQuorum` checks a mon rank against the quorum rank list.

Control flow: the function reads `testClient.Status`, logs it, then validates monitors, OSDs, manager availability, and placement group cleanliness. It fails fast on empty quorum, mon not in quorum, zero OSDs, any OSD not up/in, unavailable MGRs, or PG states not entirely `active+clean` when PGs exist.

State and persistence behavior: read-only; it observes Ceph cluster state but does not mutate Kubernetes or Ceph.

Dependencies and integration points: depends on Ceph status structures from `pkg/daemon/ceph/client` and `TestClient.Status`, which in turn uses the toolbox/cluster admin context.

Risks: health criteria are strict and may not fit transitional operator states. It requires at least one OSD, so it is incompatible with configurations intentionally skipping OSD creation. PG health only treats exactly `active+clean` as healthy, which can flag expected transient or mixed states.

Test signals: a passing result indicates monitors are in quorum, OSDs are all up/in, managers are available, and PGs are clean. Failures include enough status data in error messages to drive log collection.
