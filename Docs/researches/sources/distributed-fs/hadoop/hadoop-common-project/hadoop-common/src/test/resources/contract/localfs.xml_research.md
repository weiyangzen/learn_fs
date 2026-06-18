# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/localfs.xml

## Purpose
`localfs.xml` defines filesystem contract expectations for Hadoop's checksummed local filesystem. It captures semantics that differ from raw local disk, especially checksum handling and append behavior.

## Important Properties
The file declares case sensitivity and Unix permissions as true, disables root tests, sets `fs.contract.test.random-seek-count=1000`, and enables rename-created destination directories, rename overwrite, and empty-destination-directory removal. It marks append unsupported because checksummed filesystems do not support append, while atomic directory delete, atomic rename, seek, seek on closed file, settimes, getfilestatus, and vector early EOF check are supported. Block locality, concat, and strict exceptions are false, and seek past EOF is rejected. `supports-settimes` and `supports-getfilestatus` appear twice with the same true value.

## Control Flow
Contract tests consume these values through `Configuration` and choose which generic tests to run or which behavior to assert. The duplicate properties rely on Hadoop configuration's normal repeated-key handling; because the values agree, the duplication is harmless but noisy.

## State And Persistence
The file is a static test resource and creates no state. It points tests at local filesystem semantics that may still vary by OS for case sensitivity and permission enforcement, despite comments noting runtime OS determination.

## Dependencies And Integration Points
It integrates with local filesystem contract tests and Hadoop's `LocalFileSystem` behavior. It is related to `rawlocal.xml`, but differs on append and EOF-seek expectations due to checksum wrappers.

## Risks
The main risk is platform-dependent behavior. Case sensitivity and Unix permissions can be different on Windows or mounted filesystems, so hard-coded true values can be brittle if runtime overrides do not adjust them. Duplicate properties can obscure future edits if only one copy is changed.

## Test Signals
Signals include generic contract failures for append, rename, seek past EOF, timestamp setting, and vector IO early EOF handling. Failures that appear only on specific OSes usually indicate fixture/platform mismatch rather than core API breakage.
