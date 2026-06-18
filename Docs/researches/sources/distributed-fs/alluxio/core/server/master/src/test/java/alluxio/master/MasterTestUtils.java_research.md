# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/MasterTestUtils.java

Purpose: central helper for creating `CoreMasterContext` instances in unit tests with lightweight journal, metastore, safe-mode, backup, and UFS components.

Important APIs/types/functions: overloaded `testMasterContext` methods accepting journal system, user state, primary selector, block store factory, and inode store factory.

Control flow: simple overloads funnel to the full builder call. Defaults are `NoopJournalSystem`, heap block/inode stores, `AlwaysStandbyPrimarySelector` or `AlwaysPrimaryPrimarySelector` depending on overload, mocked `BackupManager`, `TestSafeModeManager`, start time/port `-1`, and new `MasterUfsManager`.

State and persistence: constructs in-memory contexts. Journal behavior depends on the supplied `JournalSystem`, but defaults are no-op.

Dependencies/integration: used widely by block, file, metastore, backup, and metrics master tests to avoid duplicating context setup.

Risks: default primary selector differs by overload, so tests must choose carefully. Mocked backup manager and test safe mode manager may hide behavior that full process tests need.

Test signals: consumers validate it indirectly. Direct tests would verify builder fields and supplied factories/selectors are preserved.
