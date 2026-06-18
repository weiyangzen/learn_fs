<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/RegistryOperationsClient.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/RegistryOperationsClient.java

## Purpose

ZooKeeper-backed registry client service facade. The source was read as a complete 55-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RegistryOperationsClient extends RegistryOperationsService`, `public RegistryOperationsClient(String name)`, `public RegistryOperationsClient(String name,`.

## Control Flow

Constructors delegate to RegistryOperationsService with optional RegistryBindingSource.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`, `RegistryBindingSource`, `RegistryOperationsService`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Behavior is inherited; risks are in external ZK auth/session configuration rather than this wrapper.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/RegistryOperationsClient.java -->
