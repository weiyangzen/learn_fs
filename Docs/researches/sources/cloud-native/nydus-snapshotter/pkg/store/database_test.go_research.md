<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/database_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/store/database_test.go

Purpose: validates the BoltDB store and compatibility migration behavior for daemon and RAFS records.

Important tests/helpers: `Test_daemon` covers daemon insertion, duplicate rejection, deletion, walking, and cleanup. `TestLegacyRecordsMultipleDaemonModes` writes a legacy top-level `daemons` bucket with two fusedev dedicated records, opens the new database, and verifies migrated daemon states and RAFS instances. `TestLegacyRecordsSharedDaemonModes` writes fscache shared-mode legacy records and verifies one shared daemon, two RAFS instances, and redirected config files. Helpers include `prepareCompatTestConfig`, `writeLegacyDatabase`, `writeConfigFile`, `listDaemons`, and `listRafsInstances`.

Control flow and state: tests build temporary roots, manually seed legacy Bolt buckets, then rely on `NewDatabase` to trigger `initDatabase` migration/upgrade. They inspect results through public walkers rather than private buckets.

Dependencies/integration: uses bbolt directly to create old-format data and `config.ProcessConfigurations` to seed global config mode assumptions.

Risks and test signals: tests cover happy-path legacy records but not missing optional pointer fields, corrupted JSON, version key edge cases, or duplicate records generated during migration. They give strong regression signals for schema conversion and daemon mode inference.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/store/database_test.go -->
