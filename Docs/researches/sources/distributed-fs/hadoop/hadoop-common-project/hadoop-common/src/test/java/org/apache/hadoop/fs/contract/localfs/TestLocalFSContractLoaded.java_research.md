# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractLoaded.java

## Purpose
`TestLocalFSContractLoaded` is a focused sanity test ensuring local FS contract resources are available and populated.

## Important APIs, Types, And Functions
It extends `AbstractFSContractTestBase`, creates `LocalFSContract`, and defines `testContractWorks()` plus `testContractResourceOnClasspath()`.

## Control Flow
Base setup initializes local FS. `testContractWorks()` computes the key for `SUPPORTS_ATOMIC_RENAME`, asserts it is present, and checks `isSupported()` returns true. `testContractResourceOnClasspath()` asks the classloader for `LocalFSContract.CONTRACT_XML` and asserts a URL is found.

## State And Persistence
Only inherited contract setup state is used. No files beyond the base test directory are intentionally created.

## Dependencies And Integration Points
It depends on local contract XML packaging and `AbstractFSContract` key resolution.

## Risks
Classpath/resource packaging errors can cause broad contract suites to behave incorrectly; this test isolates that failure mode.

## Test Signals
Signals are a non-null XML resource URL and a true atomic rename capability loaded from configuration.
