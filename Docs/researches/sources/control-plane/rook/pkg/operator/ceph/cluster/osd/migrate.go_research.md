# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/migrate.go

## Purpose
This file detects and stages OSD migrations required by changes to encryption settings or OSD store type. It coordinates one-at-a-time migration by deleting one OSD Deployment, saving the migrated ID in a ConfigMap, and blocking further migration until that OSD Deployment is recreated.

## Important APIs, Types, and Functions
Constants define user confirmations (`yes-really-migrate-osds`, legacy `yes-really-update-store`), the migration ConfigMap name `osd-migration-config`, and data key `osdID`. `migrationConfig` stores a map of pending OSD IDs to `OSDInfo`.

`Cluster.newMigrationConfig()` lists current OSD Deployments and populates pending migration candidates by calling `migrateForEncryption()` and `migrateForOSDStore()`. `migrateForEncryption()` maps requested device-set encryption from the CephCluster spec and compares it to each Deployment's `encrypted` label, then records mismatches. `migrateForOSDStore()` compares the Deployment `osd-store` label with `spec.Storage.GetOSDStore()`. `getOSDToMigrate()` returns and removes an arbitrary pending OSD from the map. `getOSDIds()` returns all pending IDs, used to remove them from the update queue while migration is in progress.

`saveMigrationConfig()` writes the last migrated OSD ID to a ConfigMap with the CephCluster owner reference. `isLastOSDMigrationComplete()` reads the last migrated ID and returns false until the expected `rook-ceph-osd-<id>` Deployment exists. `getLastMigratedOSDId()` reads and parses the ConfigMap, returning `-1` for missing or empty config.

## Control Flow
`Cluster.startOSDMigration()` in `osd.go` gates this file's logic behind explicit confirmation, healthy PGs, and completion of the previously migrated OSD. When candidates exist, exactly one OSD is deleted and saved as the in-progress migration. Later provisioning sees `c.migrateOSD` and allows the prepare job for that PVC to be updated.

## State and Persistence
Persistent migration state is the `osd-migration-config` ConfigMap and OSD Deployments. Deployment labels are the source of current encryption/store truth. The pending map is in-memory and recalculated from live Deployments.

## Dependencies and Integration Points
The file depends on Deployment discovery and `getOSDInfo()` from `osd.go`, Kubernetes ConfigMaps/Deployments, CephCluster storage spec, and `k8sutil.CreateOrUpdateConfigMap()`. It integrates with the main reconcile update queue to avoid upgrading OSDs that need migration.

## Risks and Edge Cases
`getOSDToMigrate()` chooses an arbitrary map entry, so migration order is nondeterministic. `migrateForEncryption()` assumes a device-set name label maps to a spec entry; missing entries yield zero-value device sets. Missing `encrypted` labels are treated as false. Store migration only considers Deployments with an `osd-store` label. A malformed ConfigMap `osdID` blocks migration with an error.

## Test Signals
`migrate_test.go` covers no-op and mismatch detection for encryption and store type, plus last-migration completion for absent ConfigMap, missing Deployment, and recreated Deployment.
