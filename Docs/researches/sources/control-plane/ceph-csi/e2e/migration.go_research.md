# sources/control-plane/ceph-csi/e2e/migration.go

Purpose: supports RBD in-tree-to-CSI migration e2e scenarios by generating migration-style volume IDs, custom cluster ID config, migration Secrets, StorageClasses, and Ceph users.

Important APIs/types/functions: `composeIntreeMigVolID(mons, rbdImageName)` creates a migration volume ID from monitor hash, image UUID, and encoded pool name. `generateClusterIDConfigMapForMigration(f, c)` computes monitor hash cluster ID, writes a custom configmap, and restarts RBD CSI pods. `createRBDMigrationSecret()`, `createMigrationUserSecretAndSC()`, `createMigrationSC()`, `createProvNodeCephUserAndSecret()`, `deleteProvNodeMigrationSecret()`, `setupMigrationCMSecretAndSC()`, and `tearDownMigrationSetup()` manage secrets, users, storageclass, config, and cleanup.

Control flow: setup fetches monitors, hashes them to the in-tree migration cluster ID, updates the configmap, restarts RBD CSI pods, creates provisioner/node Ceph users with migration caps, writes migration-format Secrets where `key` replaces `userKey` and non-admin users become `adminId`, then creates an RBD StorageClass with migration-specific secret references and `migration=true`. Teardown restores the normal configmap and deletes migration Secrets.

State and persistence: mutates the shared Ceph-CSI ConfigMap, restarts CSI pods, creates Kubernetes Secrets, creates Ceph users, and creates/deletes a StorageClass. It relies on global RBD pool, namespace, secret names, and deployment metadata.

Dependencies and integration points: uses RBD helpers (`createRBDStorageClass`, `createRBDSecret`-style Secret templates, `rbdProvisionerCaps`, `rbdNodePluginCaps`), Ceph user helpers, configmap helpers, monitor hash helpers, and Kubernetes client-go. It is part of migration test setup rather than a standalone Ginkgo suite.

Risks: `composeIntreeMigVolID()` assumes `rbdImageName` contains `intreeVolPrefix`; missing prefix will panic on `imageUID[0]`. ConfigMap changes require pod recreation and can disrupt parallel tests. Secret deletion does not ignore NotFound. Ceph users created for migration are not explicitly deleted here, only their Secrets.

Test signals: expected migration volume IDs match CSI migration parser expectations, custom configmap cluster ID resolves monitors, RBD CSI pods restart successfully, migrated provisioning works with new secrets, and teardown restores normal config and removes migration Secrets.
