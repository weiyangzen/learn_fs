# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/rawlocal.xml

## Purpose
`rawlocal.xml` defines contract-test capabilities for Hadoop's raw local filesystem, where operations map more directly to local disk without the checksum wrapper.

## Important Properties
It marks case sensitivity, Unix permissions, append, atomic directory delete, atomic rename, rename-created destination directories, rename overwrite, empty-directory destination removal, seek, seek on closed file, settimes, getfilestatus, content check, hflush, hsync, metadata update on hsync, and vector overlapping ranges as supported. It disables root tests, sets random seek count to 1000, marks block locality and concat unsupported, sets strict exceptions false, and says seek past EOF is not rejected.

## Control Flow
There is no local execution logic. Contract test classes load the file and use `fs.contract.*` booleans to decide which assertions are meaningful for raw local filesystem implementations.

## State And Persistence
The XML is persistent test metadata only. Runtime state is in temporary local files created by the contract tests, not in this resource.

## Dependencies And Integration Points
It integrates with tests for `RawLocalFileSystem` and generic filesystem contracts. The hflush/hsync flags connect it to output stream sync semantics and metadata-update assertions that are not expected of all filesystems.

## Risks
Raw local semantics are highly OS- and filesystem-dependent. Permissions, case sensitivity, hsync metadata behavior, and seek-past-EOF behavior can differ across platforms or mounts. Overstated capabilities can make contract tests flaky outside Linux-like environments.

## Test Signals
Important signals are contract tests for append, hflush/hsync, metadata durability, rename behavior, EOF seeking, content validation, and vector IO range handling.
