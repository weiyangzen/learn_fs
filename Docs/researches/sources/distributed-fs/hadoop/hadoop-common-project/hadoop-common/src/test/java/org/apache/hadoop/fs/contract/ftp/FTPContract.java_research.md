# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/FTPContract.java

## Purpose
`FTPContract` binds the generic Hadoop contract framework to the FTP filesystem. It loads FTP-specific contract options and requires a configured test directory.

## Important APIs, Types, And Functions
The class extends `AbstractBondedFSContract`, defines `CONTRACT_XML = "contract/ftp.xml"` and `TEST_FS_TESTDIR = "test.ftp.testdir"`, returns scheme `ftp`, and implements `getTestPath()` from the configured test directory.

## Control Flow
Construction loads `contract/ftp.xml`. During base setup, `AbstractBondedFSContract` initializes from configuration, then `getTestPath()` reads `test.ftp.testdir`, asserts it is present, and returns it as a Hadoop `Path`.

## State And Persistence
There is no meaningful mutable state beyond unused private fields. Persistent state is on the configured FTP server under the test directory.

## Dependencies And Integration Points
FTP contract test classes instantiate this contract. It depends on external FTP configuration and the `FTPFileSystem` implementation selected by Hadoop configuration.

## Risks
Missing `test.ftp.testdir` fails setup. A misconfigured FTP URI or credentials can run tests against the wrong server or fail before contract behavior is exercised.

## Test Signals
Setup should load FTP contract options, resolve an `ftp` filesystem, and create/delete files below the configured FTP test directory.
