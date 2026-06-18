<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/NoPathPermissionsException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/NoPathPermissionsException.java

## Purpose

RegistryIOException subtype for path permission failures. The source was read as a complete 45-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class NoPathPermissionsException extends RegistryIOException`, `public NoPathPermissionsException(String path, Throwable cause)`, `public NoPathPermissionsException(String path, String error)`, `public NoPathPermissionsException(String path, String error, Throwable cause)`, `public NoPathPermissionsException(String message,`.

## Control Flow

Supports path/cause, path/error, path/error/cause, and wrapping PathIOException while preserving path.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `PathIOException`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Class comment is incomplete; behavior relies on PathIOException formatting.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/NoPathPermissionsException.java -->
