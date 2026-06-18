<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/RegistryIOException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/RegistryIOException.java

## Purpose

Base checked exception for registry I/O failures with path context. The source was read as a complete 58-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RegistryIOException extends PathIOException`, `public RegistryIOException(String message, PathIOException cause)`, `public RegistryIOException(String path, Throwable cause)`, `public RegistryIOException(String path, String error)`, `public RegistryIOException(String path, String error, Throwable cause)`.

## Control Flow

Extends PathIOException and can wrap another PathIOException while propagating its path.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`, `PathIOException`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Correct path propagation is important for CLI diagnostics and automated cleanup.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/RegistryIOException.java -->
