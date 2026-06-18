# sources/control-plane/ceph-csi/internal/rbd/migration.go

## Purpose
Supports deletion and resolution of Kubernetes in-tree-to-CSI migrated RBD volume IDs, which encode monitor hash, image UUID, and pool name differently from native CSI IDs.

## Important APIs, Types, And Functions
`isMigrationVolID` checks for required migration markers. `parseMigrationVolID` decodes the handle into a `migrationVolID` containing image name, pool name, and cluster ID. `deleteMigratedVolume` resolves and deletes the migrated image. `genVolFromMigVolID` builds and connects an `rbdVolume` from parsed migration fields.

## Control Flow
Parsing splits the handle on the migration field separator, decodes the hex-encoded pool portion, extracts image suffix and monitor/cluster hash fields by prefix, then validates required fields. Deletion creates an RBD volume from the parsed handle, connects using monitors from CSI config, deletes the image, and logs delete failures.

## State And Persistence
The parser itself is stateless. `deleteMigratedVolume` mutates backend Ceph state by deleting the referenced RBD image but does not use native CSI OMAP reservations for migrated IDs.

## Dependencies And Integration Points
Used by `DeleteVolume` in `controllerserver.go` before normal CSI ID resolution. Depends on migration constants/types from other RBD files, util monitor lookup, credentials, and RBD errors.

## Risks And Test Signals
Risks include permissive substring checks in `isMigrationVolID`, malformed split fields, hex decode mapping to misleading missing-pool errors, and delete behavior that bypasses native CSI journal cleanup. `migration_test.go` covers valid/invalid identification and parsing cases.
