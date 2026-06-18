<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryOperations.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryOperations.java

## Purpose

Public registry service API for path creation, binding, resolving, stat/list/delete, existence, and write-accessor management. The source was read as a complete 182-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public interface RegistryOperations extends Service`, `public void clearWriteAccessors();`.

## Control Flow

Extends Hadoop Service; methods define checked exceptions for missing paths, invalid records, non-empty directories, and auth/write-accessor operations.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`, `FileAlreadyExistsException`, `PathIsNotEmptyDirectoryException`, `PathNotFoundException`, `Service`, `InvalidPathnameException`, `InvalidRecordException`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Implementations must preserve path and overwrite semantics or callers like RegistryCli and RegistryUtils will report misleading errors.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryOperations.java -->
