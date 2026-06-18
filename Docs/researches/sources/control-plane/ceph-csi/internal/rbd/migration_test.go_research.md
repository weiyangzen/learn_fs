# sources/control-plane/ceph-csi/internal/rbd/migration_test.go

## Purpose
Unit-tests recognition and parsing of migrated in-tree RBD volume IDs.

## Important APIs, Types, And Functions
`TestIsMigrationVolID` checks valid and invalid marker/prefix combinations. `TestParseMigrationVolID` checks valid handles, missing monitor/image/pool fields, disallowed migration version strings, unallowed image names, missing monitor prefix, and pool names containing underscores.

## Control Flow
Both tests are table-driven and parallel. Parsing tests compare returned `migrationVolID` structs with `reflect.DeepEqual` and verify expected error presence.

## State And Persistence
No persistent state is used. Tests only parse static strings and do not resolve monitors or connect to Ceph.

## Dependencies And Integration Points
The tests protect the migration path used by controller delete for migrated volume handles. They depend on migration constants and `migrationVolID` field semantics.

## Risks And Test Signals
The tests provide good coverage for string-shape regressions but do not cover `genVolFromMigVolID` monitor lookup or actual deletion. They also do not assert exact sentinel errors for each malformed input.
