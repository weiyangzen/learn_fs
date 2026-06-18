<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/DNSOperationsFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/DNSOperationsFactory.java

## Purpose

Factory for DNSOperations implementations. The source was read as a complete 78-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public final class DNSOperationsFactory implements RegistryConstants`, `public enum DNSImplementation`, `public static DNSOperations createInstance(Configuration conf)`, `public static DNSOperations createInstance(String name,`.

## Control Flow

createInstance validates non-null Configuration and currently instantiates RegistryDNS for DNSJAVA.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `Preconditions`, `Configuration`, `RegistryDNS`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

The operations.init(conf) call is commented out, so callers must know whether returned services need explicit init before start.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/DNSOperationsFactory.java -->
