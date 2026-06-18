# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterFactory.java

## Purpose
`FileSystemMasterFactory` creates and registers the core file-system master during master startup. It is the factory implementation used by the master registry to wire `DefaultFileSystemMaster` with its required block master and core context.

## Important APIs, types, and functions
The class implements `MasterFactory<CoreMasterContext>`. `isEnabled()` always returns true. `getName()` returns `Constants.FILE_SYSTEM_MASTER_NAME`. `create(MasterRegistry, CoreMasterContext)` retrieves `BlockMaster`, constructs `DefaultFileSystemMaster`, registers it under `FileSystemMaster.class`, and returns it.

## Control flow
Startup code invokes the factory, the factory logs creation, obtains the block master dependency from the registry, creates the default implementation, and adds it back to the registry for later lookup by RPC handlers and other services.

## State and persistence behavior
The factory has no mutable state. Persistence behavior is delegated to `DefaultFileSystemMaster` and the provided `CoreMasterContext`.

## Dependencies and integration points
It depends on `MasterRegistry`, `CoreMasterContext`, `BlockMaster`, Alluxio constants, and `DefaultFileSystemMaster`. It integrates with the master bootstrapping sequence and service registration.

## Risks
Factory creation assumes `BlockMaster` is already registered. Changing registration order or the registry key would break downstream lookups. Because `isEnabled()` is unconditional, disabling the file-system master requires a higher-level configuration mechanism rather than this factory.

## Test signals
Startup and registry tests should confirm the factory name, enabled status, block-master dependency lookup, registration of `FileSystemMaster.class`, and construction with the expected context.
