# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/LocalFSContract.java

## Purpose
`LocalFSContract` describes Hadoop's checksummed local filesystem for the contract test framework. It loads `contract/localfs.xml`, obtains a local filesystem instance, and adjusts capabilities for platform differences.

## Important APIs, Types, And Functions
Key methods are `getContractXml()`, `init()`, `adjustContractToLocalEnvironment()`, `getLocalFS()`, `getTestFileSystem()`, `getScheme()`, `getTestPath()`, and `getTestDataDir()`. `CONTRACT_XML` names the default contract resource, and `testDataDir` comes from `FileSystemTestHelper`.

## Control Flow
Construction registers the contract XML. `init()` calls `super.init()`, creates `fs` via `FileSystem.getLocal(getConf())`, then updates configuration for Windows and macOS case sensitivity/permission behavior. `getTestPath()` qualifies the test data directory against the filesystem.

## State And Persistence
The contract stores the local `FileSystem` and test data root string. Persistent state is real local files under the Hadoop test root.

## Dependencies And Integration Points
It integrates with `AbstractFSContract`, `FileSystemTestHelper`, `Shell.WINDOWS`, `ContractOptions`, and many localfs test subclasses.

## Risks
Platform adjustment is essential: NTFS and default HFS+ differ from POSIX case and permission expectations. The checked local filesystem wraps raw local IO with checksum side files, so tests must distinguish local vs raw local behavior.

## Test Signals
Signals include a `file` scheme filesystem, valid test directory qualification, and expected platform-specific contract flags in configuration.
