# sources/control-plane/rook/pkg/operator/ceph/cluster/cluster_test.go

Purpose: tests core helper behavior from `cluster.go`: pre-start validation, msgr2 config, post-mgr CRUSH cleanup, telemetry reporting, cluster full-ratio settings, secret-sourced Ceph config, and initial CephX status.

Important APIs and tests: `TestPreClusterStartValidation` covers monitor defaults, node-count validation, floating mons, and stretch cluster zone/arbiter rules. `TestConfigureMsgr2` uses a mock executor and parses generated INI config for encryption/compression/rbd map options. `TestPostMgrStartupActionsCleansUnusedCrushRules` and the disabled variant validate `ROOK_DELETE_UNUSED_CRUSH_RULES`. `TestTelemetry` checks reported config-key values for normal and external clusters. `TestClusterFullSettings` verifies ratio commands are issued only when desired values differ enough. `TestFetchCephConfigFromSecrets` covers success and error cases. `Test_initClusterCephxStatus` covers initialized, uninitialized, nonzero, and canceled contexts.

Control flow: tests build fake cluster objects and fake executors so they can assert Ceph command inputs without a real cluster. The msgr2 test intercepts `config assimilate-conf` and config removal/get commands. Telemetry tests mutate fake pods to verify node-count reporting. CephX status tests use fake controller-runtime clients to inspect status changes after retry-on-conflict updates.

State and persistence behavior: validates generated Ceph config content, Ceph config-key write attempts, status mutations on `CephCluster.Status.Cephx`, and fake Kubernetes Secret reads. No real Kubernetes or Ceph state is touched.

Dependencies and integration points: uses fake Kubernetes clientsets, fake controller-runtime client, Rook test helpers, mocked Ceph executor, INI parsing, Rook Ceph API types, and Ceph client test cluster info.

Risks: several tests depend on command argument positions and mocked outputs, which is appropriate for regressions but can be brittle during refactors. Some branches, like full local cluster orchestration and actual monitor/mgr/OSD startup, remain integration-level and are not covered here.

Test signals: broad helper-level coverage with meaningful command and status assertions. It complements `cephx_test.go`, which covers admin rotation in more detail.
