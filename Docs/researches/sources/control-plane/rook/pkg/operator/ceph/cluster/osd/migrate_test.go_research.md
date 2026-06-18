# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/migrate_test.go

## Purpose
This file tests migration candidate detection and last-migration completion logic from `migrate.go`.

## Important APIs, Types, and Helpers
`TestMigrateForEncryption` creates fake OSD Deployments with device-set and `encrypted` labels, configures requested `StorageClassDeviceSet.Encrypted`, and verifies whether `migrationConfig.osds` is populated. `TestMigrationForOSDStore` creates Deployments with `osd-store` labels and compares them against `spec.Storage.Store.Type`. `createMigrationConfigmap()` writes the migration ConfigMap used by completion tests. `TestIsLastOSDMigrationComplete` verifies behavior when the ConfigMap is absent, when it references an OSD whose Deployment is not up, and when that Deployment exists.

## Control Flow Covered
Encryption tests cover a no-op case where requested and actual encryption are true, and a mismatch case where requested true versus actual false adds osd.1. Store tests cover matching store labels and a mismatch that adds osd.1. Completion tests cover `getLastMigratedOSDId()` returning `-1` for missing state, false when the expected Deployment does not exist, and true after the Deployment is created.

## State and Persistence Behavior
Fake Kubernetes Deployments and ConfigMaps represent all persistent state. The tests reuse a fake clientset and switch namespaces between subtests to isolate cases. Deployment labels are the source of actual settings; the ConfigMap data key `osdID` is the persisted migration cursor.

## Dependencies and Integration Points
The tests depend on fake client-go, CephCluster spec types, `cephclient.ClusterInfo`, and package helpers such as `getDummyDeploymentOnNode()` and `createDeploymentOrPanic()` from other test files in the package. They indirectly exercise `getOSDInfo()` because migration detection records full `OSDInfo` for candidate Deployments.

## Risks and Gaps
`TestMigrationForOSDStore`'s no-op subtest calls `migrateForEncryption()` instead of `migrateForOSDStore()`, which appears unintended and weakens store no-op coverage. The tests do not cover malformed migration ConfigMap data, missing device-set spec entries, duplicate candidates from encryption and store checks, or nondeterministic `getOSDToMigrate()` ordering. They also do not exercise `saveMigrationConfig()` owner-reference behavior.

## Test Signals
The file gives useful coverage for basic candidate selection and migration cursor completion, but has notable gaps around error handling and one likely copy-paste issue in the store no-op test.
