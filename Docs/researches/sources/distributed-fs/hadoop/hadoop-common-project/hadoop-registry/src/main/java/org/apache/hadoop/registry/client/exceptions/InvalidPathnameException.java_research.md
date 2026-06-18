<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/InvalidPathnameException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/InvalidPathnameException.java

## Purpose

RegistryIOException subtype for invalid registry path strings. The source was read as a complete 40-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class InvalidPathnameException extends RegistryIOException`, `public InvalidPathnameException(String path, String message)`, `public InvalidPathnameException(String path,`.

## Control Flow

Constructors preserve the failing path plus message/cause.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Should be thrown after path validation helpers rather than generic IllegalArgumentException for user-facing operations.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/InvalidPathnameException.java -->
