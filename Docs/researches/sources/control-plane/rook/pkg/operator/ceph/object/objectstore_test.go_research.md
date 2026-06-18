# sources/control-plane/rook/pkg/operator/ceph/object/objectstore_test.go

Purpose: broad unit test coverage for object-store lifecycle helpers, shared-pool configuration, realm key secret handling, endpoint comparison, dashboard user management, and object pool validation.

Important APIs/tests: `TestReconcileRealm`, `TestConfigureStoreWithSharedPools`, `TestDeleteStore`, `TestGetObjectBucketProvisioner`, `TestCheckDashboardUser`, `TestDashboard`, `Test_createMultisite`, `Test_createMultisiteConfigurations`, `TestGetRealmKeySecret`, `TestGetRealmKeyArgsFromSecret`, `TestGetRealmKeyArgs`, `TestUpdateZoneEndpointList`, `TestListsAreEqual`, `TestValidateObjectStorePoolsConfig`, and `Test_sharedPoolsExist`. Large JSON constants model RGW zone and zonegroup command output.

Control flow: tests use `exectest.MockExecutor` to assert specific `ceph`/`radosgw-admin` commands and return synthetic JSON or exit codes. Shared-pool tests read the temp `--infile` JSON written by production code to validate persistence flow. Multisite tests table-drive which realm/zonegroup/zone resources already exist or fail creation, then assert which command branches and commit calls happened. Endpoint and pool validation tests table-drive many list and spec combinations.

State and persistence: test state is in mocked command responses, fake Kubernetes clients/secrets, environment variables, temp config dirs, and booleans counting command calls. It validates deletion counters for pools, root pool, CRUSH rules, and erasure-code profiles.

Dependencies and integration points: covers interactions with `cephclient`, mocked executor exit codes, Kubernetes fake CoreV1 secrets, Rook test clients, Ceph version gates, environment settings `ROOK_OBC_WATCH_OPERATOR_NAMESPACE` and `ROOK_OBC_PROVISIONER_NAME_PREFIX`, and shared-pool JSON helpers.

Risks: tests encode exact command shapes and JSON samples, which is useful but can become brittle when Ceph CLI schemas evolve. Some assertions verify error string fragments with formatting oddities. Integration behavior with real Ceph daemons, concurrent pool creation, and asynchronous dashboard secret update is not exercised.

Test signals: strong regression signal for many edge cases: root pool deletion only for last store, shared pools missing each required pool, duplicate placement names, endpoint ordering, secret key missing messages, and provisioner prefix validation.
