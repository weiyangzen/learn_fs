# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/AlluxioMasterProcessEmergencyBackupTest.java

Purpose: regression tests for master startup behavior when a UFS journal is corrupt and emergency backup on corruption is disabled.

Important APIs/types/functions: `before`, `failToGainPrimacyWhenJournalCorrupted`, `failToGainPrimacyWhenJournalCorruptedHA`, and helper `corruptJournalAndStartMasterProcess`.

Control flow: setup assigns reserved RPC/web ports, temp metastore/journal directories, and disables user metrics. Each test builds a UFS journal-backed `AlluxioMasterProcess`, either single-master primary selector or controllable HA selector forced to primary. The helper formats the journal, manually writes a bad delete-file entry for a non-existing path into the file-system master's UFS journal, starts the master, expects a runtime exception containing `NoSuchElementException`, stops the process, and verifies it is stopped.

State and persistence: manipulates real temporary UFS journal files. It deliberately corrupts journal replay state, not in-memory master state.

Dependencies/integration: uses UFS journal system classes, `UfsJournalLogWriter`, `NoopMaster`, `ControllablePrimarySelector`, and port/temp-folder JUnit rules.

Risks: the test asserts on exception message content from lower-level replay, so refactors that wrap exceptions differently may require updating expectations without changing behavior.

Test signals: protects fail-fast startup on corruption when backup is disabled, for both single-master and HA-primary paths, and verifies failed startup still leaves the process stopped.
