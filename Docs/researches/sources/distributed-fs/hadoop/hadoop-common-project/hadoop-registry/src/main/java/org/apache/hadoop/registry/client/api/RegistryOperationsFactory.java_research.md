<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryOperationsFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryOperationsFactory.java

## Purpose

Factory for authenticated/anonymous/Kerberos registry clients. The source was read as a complete 160-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public final class RegistryOperationsFactory`, `public static RegistryOperations createInstance(Configuration conf)`, `public static RegistryOperations createInstance(String name, Configuration conf)`, `public static RegistryOperationsClient createClient(String name,`, `public static RegistryOperations createAnonymousInstance(Configuration conf)`, `public static RegistryOperations createKerberosInstance(Configuration conf,`, `public static RegistryOperations createKerberosInstance(Configuration conf,`, `public static RegistryOperations createAuthenticatedInstance(Configuration conf,`.

## Control Flow

Creates RegistryOperationsClient, sets auth-related Configuration keys, validates digest id/password, initializes clients, and converts ServiceStateException causes to RuntimeException.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `Preconditions`, `StringUtils`, `Configuration`, `ServiceStateException`, `RegistryOperationsClient`, `*`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

It mutates the caller-provided Configuration; missing digest credentials fail fast with IllegalArgumentException.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryOperationsFactory.java -->
