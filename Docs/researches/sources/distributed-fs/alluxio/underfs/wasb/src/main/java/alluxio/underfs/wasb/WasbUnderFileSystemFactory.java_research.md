# sources/distributed-fs/alluxio/underfs/wasb/src/main/java/alluxio/underfs/wasb/WasbUnderFileSystemFactory.java

## Purpose
`WasbUnderFileSystemFactory` registers Azure Blob Storage UFS support for `wasb://` and `wasbs://` paths.

## APIs and Control Flow
`create` checks that `path` is non-null and delegates to `WasbUnderFileSystem.createInstance`. `supportsPath` returns true for non-null paths starting with `Constants.HEADER_WASB` or `Constants.HEADER_WASBS`.

## State, Dependencies, and Integration
The factory is stateless and thread-safe. It depends on Alluxio URI construction, UFS configuration, and factory registry conventions.

## Risks and Test Signals
The factory performs no credential validation; Hadoop Azure initialization is responsible for later failures. `WasbUnderFileSystemFactoryTest` validates registry discovery for both schemes and rejection of an `alluxio://` path.
