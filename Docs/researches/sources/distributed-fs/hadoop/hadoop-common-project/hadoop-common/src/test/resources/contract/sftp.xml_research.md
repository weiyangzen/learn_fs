# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/sftp.xml

## Purpose
`sftp.xml` is the filesystem contract-test profile for SFTP-backed filesystems. It is similar to the FTP contract but differs on seek support.

## Important Properties
The fixture disables root tests, declares case sensitivity true, append false, atomic directory delete true, atomic rename true, block locality false, concat false, seek true, seek-past-EOF rejected true, strict exceptions true, and Unix permissions false.

## Control Flow
The file is read by the contract test harness. Tests use the capability flags to include or exclude generic filesystem behavior checks for SFTP.

## State And Persistence
It stores only static XML properties. Test state is external: temporary paths on the SFTP server and any credentials/server details configured elsewhere.

## Dependencies And Integration Points
It integrates with Hadoop's SFTP filesystem implementation and generic contract tests. It depends on an accessible SFTP environment when those tests are enabled.

## Risks
SFTP servers can vary in rename atomicity, permission reporting, and seek implementation. If the configured server does not match this profile, tests may fail for environmental reasons. Root tests remain disabled to avoid destructive assumptions.

## Test Signals
Contract tests around seek, EOF rejection, atomic rename/delete, and strict exceptions are the primary signals that this fixture still matches the target SFTP implementation.
