<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/InvalidRecordException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/InvalidRecordException.java

## Purpose

RegistryIOException subtype for malformed service record data. The source was read as a complete 41-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class InvalidRecordException extends RegistryIOException`, `public InvalidRecordException(String path, String error)`, `public InvalidRecordException(String path,`.

## Control Flow

Constructors preserve path plus parse/validation detail.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Used by JSON and endpoint validators; broad catches may hide corrupt registry data if only logged.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/exceptions/InvalidRecordException.java -->
