<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/pom.xml

## Purpose

Maven module descriptor for hadoop-registry. The source was read as a complete 338-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: No public callable members beyond constants/package documentation..

## Control Flow

Declares dependencies on Hadoop common/auth, ZooKeeper/Curator, commons libs, Jackson, dnsjava, metrics, Snappy, JUnit; configures resources, SpotBugs exclusions, RAT, version-info, test-jar, Surefire env/system properties, and dist assembly profile.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

No imports; this file is self-contained at compile time. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Build/test behavior depends on inherited properties and test environment variables; SpotBugs filter and Surefire excludes are integration-sensitive.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/pom.xml -->
