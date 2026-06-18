# subset-b-008091 Research

This grouped report covers the exact source files assigned to `subset-b-008091`. Each source file has its own marker-delimited section so the report can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneHAClusterImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneHAClusterImpl.java

## Purpose

`MiniOzoneHAClusterImpl` is the in-process HA variant of Ozone's test cluster. It extends `MiniOzoneClusterImpl` and builds a single-JVM cluster containing multiple Ozone Managers, multiple Storage Container Managers, and datanodes. It exists primarily for integration and failure-mode tests that need OM HA, SCM HA, bootstrapping, leadership transfer, and active/inactive node lifecycle control.

## Important APIs and Types

- `MiniOzoneHAClusterImpl` exposes cluster accessors such as `getOzoneManager()`, `getOzoneManager(String)`, `getStorageContainerManagersList()`, `getSCM(String)`, `getOMLeader()`, `waitForLeaderOM()`, `getScmLeader(boolean)`, and active/inactive checks.
- Lifecycle APIs include `restartOzoneManagersWithConfigCustomizer`, `restartOzoneManager`, `shutdownOzoneManager`, `restartStorageContainerManager`, `stopOzoneManager`, `stopSCM`, `startInactiveOM`, and `startInactiveSCM`.
- HA expansion APIs include `bootstrapOzoneManager`, `bootstrapSCM`, `addNewOMToConfig`, `addNewSCMToConfig`, `updateOMConfigs`, and `updateSCMConfigs`.
- `Builder` configures OM/SCM counts, service IDs, active counts, low Ratis timeouts, HA address keys, metadata directories, and service startup.
- `MiniOzoneHAService<Type>` is the shared active/inactive registry used by `OMHAService` and `SCMHAService`.
- `ExitManagerForOM` converts an OM test-time exit into a cluster stop of that OM and an `IOException`.

## Control Flow

The builder validates active counts, fills defaults, enables mini-cluster metrics/store modes, initializes generic cluster configuration, adjusts OM Ratis timeouts, creates SCM service first, creates OM service second, creates datanodes, constructs the cluster, starts registered services, optionally starts datanodes, and prepares the builder for reuse. HA service creation loops retry on `BindException`; each retry stops any partially created service instances and re-runs port allocation.

For OM HA, `initOMHAConfig` writes service IDs and node lists into configuration, allocates RPC/HTTP/HTTPS/Ratis ports for each node, initializes a per-node metadata directory, calls `OzoneManager.omInit`, creates each OM, installs clients, starts only the first `numOfActiveOMs`, and records the rest as inactive. For SCM HA, `initSCMHAConfig` writes SCM service and node lists, sets the primordial SCM, allocates node-specific RPC/HTTP/HTTPS/security/Ratis/datanode/block/client/gRPC ports, initializes the first SCM with `scmInit`, bootstraps later SCMs with `scmBootstrap`, creates SCM instances, adjusts the healthy pipeline safe-mode threshold, starts active SCMs, and configures datanode addresses from active SCMs.

Leader lookup is polling-based. `getOMLeader` scans active OMs and returns a single leader only if exactly one reports `isLeaderReady`; multiple leaders return `null` so callers retry. `waitForLeaderOM` and `getScmLeader(true)` use `GenericTestUtils.waitFor` with the cluster readiness timeout. Leadership transfer removes the current leader from the list, picks the first remaining OM, calls `transferLeadership`, and waits until `getOMLeader()` reports a different node.

OM bootstrapping first freezes reload behavior for tests, captures the current leader snapshot index, builds a new configuration with a new node in the OM node list, optionally pushes that configuration to active OMs, creates the new OM in `BOOTSTRAP` or `FORCE_BOOTSTRAP` mode, registers it inactive, starts it, updates the cluster configuration, waits for the new OM's Ratis snapshot index to catch up, and optionally verifies peer-list propagation. SCM bootstrapping mirrors that flow with SCM-specific configuration and SCM Ratis snapshot checks.

## State and Persistence

Cluster state is held in the inherited configuration, `clusterMetaPath`, `OMHAService`, and `SCMHAService`. Each OM and SCM gets its own metadata subdirectory under the cluster path or node-specific path. HA service state is in-memory maps/lists tracking all services plus active and inactive subsets; this registry is not thread-safe and is suitable for test control paths, not production synchronization.

Persistent state belongs to the embedded services themselves: OM metadata DB/Ratis state under per-node `OZONE_METADATA_DIRS`, SCM metadata/Ratis state under per-node SCM directories, and datanode state from the parent cluster. Bootstrap methods mutate both service process state and configuration state; if a bind failure happens after active service configs were updated, the code resets existing service configurations to the previous cluster config.

## Dependencies and Integration Points

The class integrates with `OzoneManager`, `StorageContainerManager`, Ratis, `HddsTestUtils`, `SCMConfigurator`, `DatanodeStoreCache`, `DefaultMetricsSystem`, `OzoneClientFactory`, `OzoneManagerRatisServer`, `ConfUtils`, HDDS/OM/SCM config keys, `GenericTestUtils`, and port allocation helpers. It relies on the parent `MiniOzoneClusterImpl` for datanode creation, common service startup, client wiring, stopping OMs, and overall cluster shutdown.

## Risks and Edge Cases

There is heavy reliance on dynamically allocated local ports; retry loops handle bind conflicts but can spin until allocation succeeds. `MiniOzoneHAService` creates `services` from `HashMap.values()`, so service ordering can be non-deterministic despite index-based accessors. Some lifecycle calls manipulate active/inactive lists directly and assume single-threaded test usage. `bootstrapSCM` places readiness/config-update waits inside the retry loop after the catch block, which means a successful `break` exits before those waits; that is a control-flow risk worth verifying against tests. `waitForConfigUpdateOnActiveSCMs` checks `scm.doesPeerExist(scm.getScmId())` for each active SCM instead of the new SCM node ID, which may be intentional or a bug. `transferOMLeadershipToAnotherNode` mutates the list returned by `getOzoneManagersList`, so it can remove the current leader from cluster state if that list is the live backing list.

## Test Signals

This file is itself test infrastructure. The strongest signals are expected from HA mini-cluster integration tests that exercise bind retry, OM/SCM leader election, active/inactive startup, restart, bootstrap, force bootstrap, listener OMs, SCM bootstrap, peer propagation, and shutdown. Risky areas need tests that assert service ordering, no accidental list mutation during leadership transfer, post-bootstrap peer visibility, and SCM bootstrap wait behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneHAClusterImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/UniformDatanodesFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/UniformDatanodesFactory.java

## Purpose

`UniformDatanodesFactory` is a `MiniOzoneCluster.DatanodeFactory` that produces per-datanode configurations with consistent layout, volume count, reserved space, version settings, and short timing defaults. It is used by mini-cluster tests that need datanodes with predictable topology and storage characteristics.

## Important APIs and Types

- `apply(OzoneConfiguration)` clones the base configuration and returns a datanode-specific configuration.
- `configureDatanodePorts(ConfigurationTarget)` assigns loopback hostnames and free ports for HTTP, client, IPC, Ratis IPC/admin/server/datastream, and replication server ports.
- `Builder` exposes `setNumDataVolumes`, `setReservedSpace`, `setLayoutVersion`, `setInitialVersion`, `setCurrentVersion`, and `build`.

## Control Flow

Each `apply` call increments `nodesCreated`, clones the input config, allocates ports, derives a `datanode-N` base directory from `OZONE_METADATA_DIRS`, creates metadata, data, and Ratis directories, writes volume path lists and optional per-volume reserved-space strings, optionally initializes `DatanodeLayoutStorage`, optionally writes test initial/current datanode versions, and shortens leader election and heartbeat intervals.

## State and Persistence

The factory's only in-memory mutable state is an `AtomicInteger` counter. It creates real directories on disk for metadata, data volumes, and Ratis storage. Optional layout initialization persists layout metadata before the datanode service starts.

## Dependencies and Integration Points

It depends on HDDS/Ozone config keys, `DatanodeLayoutStorage`, `DatanodeVersion`, `ReplicationServer.ReplicationConfig`, and `GenericTestUtils.PortAllocator`. It integrates with `MiniOzoneCluster` by returning a complete config for each datanode service.

## Risks and Edge Cases

`OZONE_METADATA_DIRS` must be present or `Objects.requireNonNull` fails. Reserved-space strings are set to an empty string when no reserved space is configured, which downstream parsers must tolerate. The factory assumes directories can be created and ports remain free until service bind. Layout/current/initial version combinations can create upgrade/downgrade test states, so callers must choose compatible versions.

## Test Signals

Useful tests assert unique per-node directories and ports, correct number of data volumes, correct reserved-space formatting, layout metadata creation, and propagation of initial/current test versions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/UniformDatanodesFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/package-info.java

## Purpose

This package descriptor documents `org.apache.hadoop.ozone` in the mini-cluster module as the package for running Ozone in a single JVM for tests.

## Important APIs and Types

The file declares only the package and package-level Javadoc. There are no exported methods, fields, or runtime types.

## Control Flow

No runtime control flow exists.

## State and Persistence

No state is held or persisted.

## Dependencies and Integration Points

The integration point is Java package documentation generation and package-level source organization for mini-cluster classes.

## Risks and Edge Cases

The only risk is documentation drift if the package evolves beyond single-JVM mini-cluster test utilities.

## Test Signals

Compilation and Javadoc generation are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/dev-support/findbugsExcludeFile.xml

## Purpose

This SpotBugs/FindBugs exclusion file exists for the `ozone-multitenancy-ranger` module but currently contains no match rules.

## Important APIs and Types

The file defines a root `<FindBugsFilter>` element with no children.

## Control Flow

No runtime flow exists; the file is consumed by the Maven SpotBugs plugin.

## State and Persistence

No application state is affected. It persists build-analysis configuration.

## Dependencies and Integration Points

It is referenced from the module POM's `spotbugs-maven-plugin` configuration as `${basedir}/dev-support/findbugsExcludeFile.xml`.

## Risks and Edge Cases

Because the filter is empty, all SpotBugs findings in the module remain active. The main risk is future developers assuming exclusions exist when they do not.

## Test Signals

The signal is Maven SpotBugs execution using this file without XML parse failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/pom.xml

## Purpose

This Maven POM defines the `ozone-multitenancy-ranger` JAR module, the Ranger-backed implementation of Ozone Manager multitenancy integration.

## Important APIs and Types

The artifact is `org.apache.ozone:ozone-multitenancy-ranger:2.3.0-SNAPSHOT` with parent `org.apache.ozone:ozone`. It packages a JAR and names the module "Apache Ozone Multitenancy with Ranger".

## Control Flow

Build flow is standard Maven. The compiler plugin disables annotation processing with `<proc>none</proc>`. SpotBugs is configured with the module-local exclude file. Runtime dependencies include Jersey client and Ranger integration/client libraries. Provided dependencies link the module back to Hadoop/Ozone manager APIs. Test dependencies include Hadoop auth/common test jars and Ozone/HDDS test utilities.

## State and Persistence

The POM controls dependency graph and plugin state, not application state. It intentionally sets `classpath.skip` to `false`.

## Dependencies and Integration Points

The main integrations are `ranger-intg`, `ranger-plugins-common`, `jersey-client`, `hadoop-common`, `hdds-common`, `hdds-config`, `ozone-common`, and `ozone-manager`. The POM excludes many transitive artifacts from `ranger-plugins-common`, including logback, AWS/GCS connectors, Hadoop client bundles, Hive, Kafka, Lucene/Solr, Elasticsearch/OpenSearch, Jersey bundle, commons-logging, JAXB/activation, and JSON-smart, mostly to avoid classpath bloat and binding conflicts.

## Risks and Edge Cases

Ranger dependencies often pull broad transitive graphs; the exclusions are important and can break if Ranger changes artifact structure. Disabling annotation processing is appropriate for this adapter but means generated config/validator processors from OM are not run here. Provided scope requires the host Ozone distribution to supply matching Ozone/Hadoop classes.

## Test Signals

Module compile, dependency convergence/enforcer checks, SpotBugs, and the Ranger integration test class are the build signals. Because Ranger endpoint tests are marked unhealthy/manual, routine CI likely verifies mostly compilation and static analysis.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/src/main/java/org/apache/hadoop/ozone/om/multitenant/RangerClientMultiTenantAccessController.java -->
# sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/src/main/java/org/apache/hadoop/ozone/om/multitenant/RangerClientMultiTenantAccessController.java

## Purpose

`RangerClientMultiTenantAccessController` implements `MultiTenantAccessController` by translating Ozone multitenancy policies and roles to Apache Ranger model objects and invoking `RangerClient` over Ranger's admin API.

## Important APIs and Types

- Constructor reads Ranger HTTPS address, Ranger service name, OM Kerberos principal/keytab, or fallback clear-text Ranger admin credentials from configuration, then creates a `RangerClient`.
- Policy methods: `createPolicy`, `getPolicy`, `getLabeledPolicies`, `updatePolicy`, and `deletePolicy`.
- Role methods: `createRole`, `getRole`, `updateRole`, and `deleteRole`.
- `getRangerServicePolicyVersion` fetches service policy version and returns `-1` if Ranger omits it.
- Translation helpers map between Ozone `Policy`, `Role`, `Acl` and Ranger `RangerPolicy`, `RangerRole`, policy resources, policy items, role members, and ACL strings.

## Control Flow

Construction first builds ACL string lookup maps from the interface helper. It requires the Ranger HTTPS URL and service name. If both fallback username and password are configured, it uses SIMPLE auth and treats that username as the OM principal/short name. Otherwise it builds a Kerberos principal by replacing `_HOST` using the OM address hostname, requires a keytab, derives the short user name through `UserGroupInformation`, and creates a Kerberos `RangerClient`. The previous Hadoop login user is restored in a `finally` block after client construction.

Every Ranger operation logs at debug level, invokes the corresponding `RangerClient` call, catches `RangerServiceException`, decodes common HTTP status codes to actionable logs, and rethrows as `IOException`. Policy translation builds Ranger resources for volume/bucket/key if present, maps user and role ACLs into `RangerPolicyItem` entries, and maps labels/description/name/service. Reverse translation reads policy items, converts allowed/denied accesses to Ozone ACLs, assigns them to each role, maps resources by type, warns on unknown resource names, and restores metadata. Role translation handles role ID, name, description, users, createdByUser, nested roles, and role-admin flags.

## State and Persistence

The controller holds a `RangerClient`, Ranger service name, ACL lookup maps, resolved OM principal, and short user name. It does not persist local state. Durable state is in Ranger: policies, roles, memberships, labels, and service policy version.

## Dependencies and Integration Points

It depends on Ozone OM config keys, `OmUtils`, `OzoneConsts.OZONE`, Hadoop security/UGI, Ranger client/model classes, Jersey `ClientResponse.Status`, and the `MultiTenantAccessController` domain model. It is the concrete adapter chosen by `MultiTenantAccessController.create(conf)` when Ranger multitenancy is enabled.

## Risks and Edge Cases

Authentication validity is not checked during construction; invalid credentials surface later as repeated 401 failures. The constructor uses `Objects.requireNonNull`, so missing config becomes `NullPointerException` rather than a typed config error. The policy reverse mapper only reconstructs role ACLs, not user ACLs, even though `toRangerPolicy` emits both user and role items. Unknown ACL strings can map to `null` ACL types. SIMPLE auth requires both username and password; a partially configured fallback silently selects Kerberos and may fail later. `getRangerServicePolicyVersion` returning `-1` for null may hide privilege problems unless callers check it.

## Test Signals

The companion test class creates this controller through the factory with Kerberos-like config but is marked unhealthy because it requires a Ranger endpoint. Strong tests should mock or fake `RangerClient` to verify policy/role conversion, user ACL round-tripping, HTTP status handling, SIMPLE-vs-Kerberos selection, and null policy version behavior without needing live Ranger.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/src/main/java/org/apache/hadoop/ozone/om/multitenant/RangerClientMultiTenantAccessController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/src/main/java/org/apache/hadoop/ozone/om/multitenant/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/src/main/java/org/apache/hadoop/ozone/om/multitenant/package-info.java

## Purpose

This package descriptor documents the Ranger-backed Ozone multitenancy implementation package.

## Important APIs and Types

The file declares package-level Javadoc and the `org.apache.hadoop.ozone.om.multitenant` package. It has no runtime APIs.

## Control Flow

No runtime control flow exists.

## State and Persistence

No state is held or persisted.

## Dependencies and Integration Points

It integrates with Java package documentation and source organization for the Ranger multitenancy module.

## Risks and Edge Cases

The documentation says "Multi tenancy"; terminology should stay aligned with user-facing docs and module names.

## Test Signals

Compilation and Javadoc/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/src/main/java/org/apache/hadoop/ozone/om/multitenant/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/src/test/java/org/apache/hadoop/ozone/om/multitenant/TestRangerClientMultiTenantAccessController.java -->
# sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/src/test/java/org/apache/hadoop/ozone/om/multitenant/TestRangerClientMultiTenantAccessController.java

## Purpose

This test class adapts the shared `MultiTenantAccessControllerTests` suite to the real `RangerClientMultiTenantAccessController` implementation.

## Important APIs and Types

- Extends `MultiTenantAccessControllerTests`.
- Overrides `createSubject()` to build an in-memory configuration and return `MultiTenantAccessController.create(conf)` asserted as `RangerClientMultiTenantAccessController`.
- Annotated `@Unhealthy("Requires a Ranger endpoint")`.

## Control Flow

The test sets JVM SSL truststore and Kerberos config system properties, enables Kerberos debug logging, uses default Kerberos name rules, fills Ranger HTTPS address, Ranger service name, OM Kerberos principal, and keytab path, optionally documents SIMPLE auth settings as commented code, raises RangerClient logging to DEBUG, and creates the subject through the factory.

## State and Persistence

It mutates global JVM system properties and Kerberos name rules, which can affect other tests in the same JVM. It does not persist application data except whatever the inherited tests may create through a live Ranger endpoint.

## Dependencies and Integration Points

It depends on in-memory HDDS configuration, Hadoop Kerberos utilities, `GenericTestUtils`, `RangerClient` logging, and the abstract multitenancy test suite. It is intended for manual or unhealthy test lanes with a reachable Ranger server.

## Risks and Edge Cases

Hard-coded placeholder paths and localhost Ranger URL mean the test fails without environment-specific setup. Global Kerberos/SSL mutations can leak. The test currently covers Kerberos path only; SIMPLE auth is noted but not active.

## Test Signals

When enabled in a configured environment, it signals that factory creation, Ranger authentication setup, and inherited CRUD tests work against real Ranger. In normal CI, the `@Unhealthy` marker means it likely does not protect routine builds.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/src/test/java/org/apache/hadoop/ozone/om/multitenant/TestRangerClientMultiTenantAccessController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs-examples/libo3fs_read.c -->
# sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs-examples/libo3fs_read.c

## Purpose

`libo3fs_read.c` is a simple native example program that connects to Ozone's `o3fs` filesystem through the libo3fs wrapper and reads a file in buffer-sized chunks.

## Important APIs and Functions

- `main(int argc, char **argv)` parses command-line arguments for filename, ignored file size position, buffer size, host, port, bucket, and volume.
- Uses `o3fsConnect`, `o3fsOpenFile`, `o3fsRead`, `o3fsCloseFile`, and `o3fsDisconnect`.

## Control Flow

The program builds a usage message, validates that exactly eight arguments are present, connects to the requested `o3fs://bucket.volume.host:port`, opens the file read-only with the requested buffer size, allocates a buffer, repeatedly calls `o3fsRead` while the prior read returns a full buffer, frees the buffer, closes the file, disconnects, and exits.

## State and Persistence

It has no persistent state and reads remote object data without modifying it. Local state is the filesystem handle, file handle, and heap buffer.

## Dependencies and Integration Points

It depends on `o3fs.h`, standard C libraries, and the libo3fs/libhdfs-backed implementation. It is an example or smoke-test client for native Ozone filesystem access.

## Risks and Edge Cases

The code reads `argv[1]`, `argv[3]`, and later arguments before validating `argc`, so too few arguments can cause undefined behavior. `argv[2]` file size is documented in usage but unused. The open failure message says "for writing" while opening read-only. It does not include `errno` details, does not handle negative read returns specially, and does not print or verify read data.

## Test Signals

Manual smoke tests can validate successful connect/open/read/close against an Ozone endpoint. Static analysis should flag argument access before `argc` validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs-examples/libo3fs_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs-examples/libo3fs_write.c -->
# sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs-examples/libo3fs_write.c

## Purpose

`libo3fs_write.c` is a native example program that writes patterned data to an Ozone `o3fs` file through the libo3fs wrapper.

## Important APIs and Functions

- `main(int argc, char **argv)` parses filename, total file size, buffer size, host, port, bucket, and volume.
- Uses `o3fsConnect`, `o3fsOpenFile`, `o3fsWrite`, `o3fsCloseFile`, and `o3fsDisconnect`.

## Control Flow

The program validates argument count after assigning variables from `argv`, connects to O3FS, checks parsed file size and buffer size constraints, casts buffer size to `tSize`, opens the output file write-only, allocates a buffer, fills it with repeated lowercase letters, loops until the requested file size is written in full or partial buffer chunks, validates each `o3fsWrite` return value, then frees, closes, disconnects, and exits.

## State and Persistence

It persists remote object data by writing the requested file. Local state is limited to handles, counters, and the heap buffer.

## Dependencies and Integration Points

It depends on `o3fs.h`, libhdfs-compatible type definitions, POSIX flags, and standard C library parsing/allocation. It is an example writer for native Ozone filesystem access.

## Risks and Edge Cases

The program reads `argv` before checking `argc`. It checks `errno == ERANGE` for file size without clearing `errno` before `strtoul` and stores the result in `off_t`, so overflow behavior is platform-sensitive. It uses `ULONG_MAX` without including `<errno.h>` in the source read, though `errno` is referenced. A zero buffer size would create an infinite write loop because `nrRemaining -= bufferSize` never advances. Error exits after failed writes do not free/close/disconnect.

## Test Signals

Smoke tests should write known sizes, including non-multiple buffer sizes, and then read back data. Negative tests should cover missing args, zero buffer, oversized buffer, parse overflow, failed connect, failed open, and short writes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs-examples/libo3fs_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs/o3fs.c -->
# sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs/o3fs.c

## Purpose

`o3fs.c` implements a thin libo3fs wrapper over libhdfs, constructing Ozone `o3fs://` URIs and forwarding file operations to the HDFS C API.

## Important APIs and Functions

- `o3fsConnect(host, port, bucket, vol)` creates an `hdfsBuilder`, sets the namenode URI and port, and connects.
- `o3fsOpenFile`, `o3fsRead`, `o3fsWrite`, `o3fsCloseFile`, and `o3fsDisconnect` cast opaque O3FS handles to libhdfs handles and call corresponding HDFS APIs.

## Control Flow

Connection flow allocates a builder, computes URI length, formats `o3fs://bucket.volume.host` into a stack buffer, sets the URI and port on the builder, and returns `hdfsBuilderConnect`. All other functions are direct one-call wrappers.

## State and Persistence

The wrapper itself stores no global state. Persistent effects are delegated to libhdfs/Ozone: opening, reading, writing, closing, and disconnecting remote filesystem handles.

## Dependencies and Integration Points

It depends on `o3fs.h`, `hdfs.h`, and libhdfs builder semantics. Its URI format integrates Ozone's bucket and volume naming into the host component of `o3fs://bucket.volume.host:port`.

## Risks and Edge Cases

The URI length calculation appears short by one for separators and then calls `snprintf(string, len + 3, ...)` on `char string[len + 2]`, which risks stack buffer overflow. It does not validate null host/bucket/volume inputs. Builder ownership after `hdfsBuilderConnect` is delegated to libhdfs behavior. The wrapper exposes no flush, seek, tell, append, or error-detail APIs.

## Test Signals

Unit or sanitizer tests should cover URI construction length, null handling, and connection failure. Integration tests should verify that wrapper calls behave identically to libhdfs calls for open/read/write/close/disconnect.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs/o3fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs/o3fs.h -->
# sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs/o3fs.h

## Purpose

`o3fs.h` declares the public C API for the libo3fs wrapper.

## Important APIs and Types

- `o3fsFS` and `o3fsFile` are opaque pointer typedefs mirroring libhdfs internal handle types.
- Declares `o3fsConnect`, `o3fsOpenFile`, `o3fsRead`, `o3fsCloseFile`, `o3fsDisconnect`, and `o3fsWrite`.

## Control Flow

No control flow exists in the header. It defines the compile-time contract used by examples and any native clients.

## State and Persistence

No state is stored in the header. Handles represent remote filesystem/file state managed by the implementation and libhdfs.

## Dependencies and Integration Points

The header includes `hdfs.h` for `tPort`, `tSize`, and compatible opaque structs. It is the integration boundary for C clients using Ozone's libhdfs-compatible O3FS access.

## Risks and Edge Cases

Because handle typedefs alias libhdfs internals, ABI compatibility depends on libhdfs. The API is minimal and lacks explicit error retrieval or ownership documentation beyond libhdfs conventions.

## Test Signals

Compilation of examples and consumers against this header is the main signal; ABI smoke tests should link with the implementation and libhdfs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs/o3fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/dev-support/findbugsExcludeFile.xml

## Purpose

This SpotBugs/FindBugs exclusion file configures one module-specific suppression for the Ozone Manager module.

## Important APIs and Types

It has a `<FindBugsFilter>` root with one `<Match>` targeting class `org.apache.hadoop.ozone.om.snapshot.diff.delta.TestRDBDifferComputer` and bug pattern `RV_RETURN_VALUE_IGNORED_NO_SIDE_EFFECT`.

## Control Flow

No runtime control flow exists. Maven SpotBugs consumes the filter during static analysis.

## State and Persistence

No application state is affected. It persists a build-tool suppression.

## Dependencies and Integration Points

The OM POM references this file from the `spotbugs-maven-plugin` configuration.

## Risks and Edge Cases

Suppressions can mask real issues if the target class behavior changes. The suppression is class-specific, which limits blast radius.

## Test Signals

The relevant signal is SpotBugs running cleanly with the intended warning suppressed and unrelated warnings still reported.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/pom.xml

## Purpose

This Maven POM defines the `ozone-manager` server module, which packages the Apache Ozone Manager service JAR and its runtime/build integrations.

## Important APIs and Types

The artifact is `org.apache.ozone:ozone-manager:2.3.0-SNAPSHOT` with packaging `jar`. It depends on Ozone/HDDS interfaces, server framework, RocksDB integration, Ratis, gRPC/Netty, Hadoop, Jackson, protobuf, Jetty, Reflections, AspectJ, and assorted utilities.

## Control Flow

Build flow includes annotation processing via `maven-compiler-plugin` using `ConfigFileGenerator`, `OmRequestFeatureValidatorProcessor`, and `RegisterValidatorProcessor`. The enforcer plugin overrides root restrictions to allow only selected annotation processors and bans specific imports. The dependency plugin unpacks common static web assets and docs during `prepare-package`. AspectJ compile runs through `aspectj-maven-plugin`. SpotBugs uses the module-local exclude file.

## State and Persistence

The POM controls dependency and build-plugin state, not runtime state. It affects generated config metadata, validators, packaged web resources, and static-analysis behavior.

## Dependencies and Integration Points

Major integrations are HDDS common/client/server/config/interface modules, Ozone common/client/interface/storage modules, RocksDB native/managed components, Ratis common/grpc/netty/server/proto artifacts, gRPC Netty/stub/API, Netty TLS runtime, Hadoop auth/common/HDFS client, Jetty webapp, AspectJ, and SLF4J reload4j runtime. Test dependencies bring in HDDS/Ozone test jars and compile-testing.

## Risks and Edge Cases

The module is central and dependency-heavy; transitive conflicts around Netty, Ratis, RocksDB, Hadoop, and logging are high-impact. Annotation processor configuration is part of source validation and generated config output, so accidental changes can break runtime config metadata. Unpacked web/docs resources make packaging sensitive to upstream artifact contents.

## Test Signals

Signals include full module compile with processors, unit/integration tests, enforcer checks, SpotBugs, AspectJ weaving success, and packaging checks that confirm web assets and docs are included.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/audit/OMAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/audit/OMAction.java

## Purpose

`OMAction` enumerates audit action names for user/request-level Ozone Manager operations.

## Important APIs and Types

It implements `AuditAction` and exports many enum constants covering write actions, read actions, ACL operations, filesystem operations, S3 secrets, tenants, snapshots, upgrades, object tagging, and snapshot diff jobs. `getAction()` returns `this.toString()`.

## Control Flow

There is no branching beyond enum initialization. Audit code can call `getAction()` to obtain the serialized action name.

## State and Persistence

Enum constants are static process state. Their names become audit log values and may be consumed by downstream audit tooling.

## Dependencies and Integration Points

It depends on the Ozone audit `AuditAction` interface. OM request handlers and audit emitters use these constants to tag audit events.

## Risks and Edge Cases

Renaming constants changes audit log strings and can break external parsing. Missing constants for new OM operations cause inconsistent audit coverage.

## Test Signals

Tests should verify request handlers use the expected `OMAction` constants and that new user-visible operations add audit actions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/audit/OMAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/audit/OMSystemAction.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/audit/OMSystemAction.java

## Purpose

`OMSystemAction` enumerates audit action names for system-originated Ozone Manager events that are not direct user requests.

## Important APIs and Types

It implements `AuditAction` and defines constants such as `STARTUP`, `LEADER_CHANGE`, deletion cleanup actions, checkpoint installation, snapshot purge/move/set-property events, and key/directory deletion. `getAction()` returns `this.toString()`.

## Control Flow

No runtime branching exists beyond enum use by audit emitters.

## State and Persistence

Enum constants are static. Their string values are persisted in audit logs.

## Dependencies and Integration Points

It integrates with the same `AuditAction` abstraction as request-level `OMAction`, but is intended for system audit flows such as background services and leadership events.

## Risks and Edge Cases

Renames are audit compatibility changes. Missing actions can hide system operations from audit trails.

## Test Signals

Tests or audit assertions should verify background services and OM lifecycle flows emit these actions where required.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/audit/OMSystemAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/audit/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/audit/package-info.java

## Purpose

This package descriptor documents the Ozone Manager audit action package.

## Important APIs and Types

It declares package-level Javadoc stating that the package defines `OMAction`, an `AuditAction` implementation for audited OM actions.

## Control Flow

No runtime control flow exists.

## State and Persistence

No state is held or persisted.

## Dependencies and Integration Points

It integrates with Java package documentation for OM audit classes.

## Risks and Edge Cases

The text mentions `OMAction` but not `OMSystemAction`; documentation could drift as the package expands.

## Test Signals

Compilation and Javadoc/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/audit/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/common/BekInfoUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/common/BekInfoUtils.java

## Purpose

`BekInfoUtils` provides common bucket encryption key validation and metadata enrichment for OM bucket encryption flows.

## Important APIs and Types

- `getBekInfo(KeyProviderCryptoExtension kmsProvider, BucketEncryptionInfoProto bek)` validates a KMS provider and requested key, fetches KMS metadata, warms encrypted key pools, and returns a populated `BucketEncryptionInfoProto`.

## Control Flow

The method rejects a null KMS provider with `INVALID_KMS_PROVIDER`, rejects a missing key name with `BUCKET_ENCRYPTION_KEY_NOT_FOUND`, fetches key metadata by key name, rejects missing KMS metadata with the same not-found result, warms encrypted keys for the key name, builds a new bucket encryption info proto with the key name, `ENCRYPTION_ZONES` crypto protocol version, and cipher suite converted from KMS metadata, then returns it.

## State and Persistence

The utility is stateless. It may cause KMS-side or provider-side encrypted data encryption key pools to warm, but it does not persist OM metadata itself. The returned proto is later persisted by bucket creation/update flows.

## Dependencies and Integration Points

It depends on Hadoop KMS `KeyProviderCryptoExtension`, `KeyProvider.Metadata`, Hadoop `CipherSuite`, OM `OMException`, `BucketEncryptionInfoProto`, and `OMPBHelper` conversion helpers.

## Risks and Edge Cases

`bek.getKeyName() == null` is used for validation; depending on protobuf defaults, empty strings may pass and fail only at KMS lookup. KMS latency/errors propagate as `IOException`. Warm-up failures will fail the operation. Cipher conversion depends on provider metadata containing a supported cipher name.

## Test Signals

Tests should cover null provider, missing key name, nonexistent KMS key, valid metadata conversion, KMS IOException propagation, and warm-up invocation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/common/BekInfoUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/common/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/common/package-info.java

## Purpose

This package descriptor documents common OM utility classes.

## Important APIs and Types

It declares the `org.apache.hadoop.ozone.common` package and package-level Javadoc. It has no runtime API.

## Control Flow

No runtime control flow exists.

## State and Persistence

No state is held or persisted.

## Dependencies and Integration Points

It supports package documentation for OM common utilities such as `BekInfoUtils`.

## Risks and Edge Cases

Documentation may become too broad or stale as utilities are added.

## Test Signals

Compilation and Javadoc/package checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/common/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/BucketManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/BucketManager.java

## Purpose

`BucketManager` defines the OM bucket-level management interface and extends ACL checking via `IOzoneAcl`.

## Important APIs and Types

- `getBucketInfo(volumeName, bucketName)` returns `OmBucketInfo`.
- `listBuckets(volumeName, startBucket, bucketPrefix, maxNumOfBuckets, hasSnapshot)` returns a paged list of `OmBucketInfo` for a volume, optionally filtered by prefix and snapshot presence.
- Inherited ACL methods are `getAcl` and `checkAccess`.

## Control Flow

This is an interface; implementation flow is in `BucketManagerImpl` and other possible implementations.

## State and Persistence

The interface describes access to bucket metadata persisted in OM metadata storage but holds no state.

## Dependencies and Integration Points

It depends on `OmBucketInfo`, `IOException`, and `IOzoneAcl`. OM request handlers use this abstraction for bucket reads/listings and ACL checks.

## Risks and Edge Cases

Interface semantics require callers and implementations to agree on pagination exclusivity, prefix filtering, snapshot filtering, and whether bucket links are resolved.

## Test Signals

Contract tests should cover get, list pagination, prefix filtering, snapshot filtering, and ACL behavior through concrete implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/BucketManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/BucketManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/BucketManagerImpl.java

## Purpose

`BucketManagerImpl` is the read/ACL implementation of `BucketManager` backed by `OMMetadataManager`.

## Important APIs and Types

- Constructor stores `OzoneManager` and `OMMetadataManager`.
- `getBucketInfo` reads bucket metadata under the bucket read lock.
- `listBuckets` delegates to `metadataManager.listBuckets`.
- `getAcl` validates bucket resource type, reads `OmBucketInfo`, and returns bucket ACLs.
- `checkAccess` optionally resolves bucket links, reads bucket ACLs, and evaluates them through `OzoneAclUtil.checkAclRights`.

## Control Flow

`getBucketInfo` validates arguments, acquires `BUCKET_LOCK`, calls `OzoneManagerUtils.getBucketInfo`, logs unexpected IOExceptions, and releases the lock. `getAcl` rejects non-bucket `OzoneObj`s, acquires the bucket lock, looks up the bucket table row by metadata key, throws `BUCKET_NOT_FOUND` if absent, and returns ACLs. `checkAccess` decides whether to resolve bucket links: bucket operations are resolved except DELETE, READ_ACL, and READ, while KEY and PREFIX resources are resolved. It then locks the resolved bucket, loads metadata, throws not-found when absent, checks ACL rights, logs debug results, and converts unexpected IO failures to `OMException(INTERNAL_ERROR)`.

## State and Persistence

The implementation is stateless beyond references to OM and metadata manager. It reads persisted bucket rows from OM metadata tables but does not mutate them.

## Dependencies and Integration Points

It integrates with `OzoneManager.resolveBucketLink`, `OMMetadataManager` locking/tables, `OzoneManagerUtils`, `OmBucketInfo`, `OzoneAclUtil`, `OzoneObj`, `RequestContext`, and OM exception result codes.

## Risks and Edge Cases

The link resolution rules are subtle: some bucket ACL checks intentionally operate on the source/link bucket, while writes/key/prefix checks resolve to the real bucket. If resolution fails with bucket-not-found, the code logs a warning and continues to check the original bucket; other errors become internal errors. Non-OM exceptions are logged, but OM exceptions are passed through. Correct lock release depends on all paths reaching `finally`, which the code does.

## Test Signals

Tests should cover get/list behavior, missing bucket errors, non-bucket `getAcl` rejection, ACL success/failure, link bucket resolution for key/prefix and selected bucket operations, and lock release on exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/BucketManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/BucketUtilizationMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/BucketUtilizationMetrics.java

## Purpose

`BucketUtilizationMetrics` is a Hadoop metrics source that emits per-bucket capacity and quota metrics from OM metadata.

## Important APIs and Types

- `create(OMMetadataManager)` registers a metrics source with `DefaultMetricsSystem`.
- `getMetrics(MetricsCollector, boolean)` iterates bucket metadata and emits gauges/tags.
- `unRegister()` unregisters the source.
- `BucketMetricsInfo` defines tag/gauge names and descriptions.

## Control Flow

On collection, the source obtains `metadataManager.getBucketIterator()`, skips null cache values, computes available space as `-1` when quota is unset or `max(quota - totalBucketSpace, 0)` otherwise, and adds one metrics record per bucket with volume and bucket tags plus used bytes, snapshot used bytes, quota bytes, quota namespace, and available bytes.

## State and Persistence

The class holds only an `OMMetadataManager` reference. Metrics are live observations from OM metadata/cache, not persisted by this class.

## Dependencies and Integration Points

It integrates with Hadoop metrics2, `DefaultMetricsSystem`, OM metadata bucket iterators, `OmBucketInfo`, and `OzoneConsts.OZONE` metrics context.

## Risks and Edge Cases

Metric cardinality grows with bucket count because one record is emitted per bucket. Iteration over cache/table state must tolerate deleted buckets as null cache values. The source name is class-simple-name based, so double registration without unregister can conflict.

## Test Signals

Tests should verify registration/unregistration, metrics for quota/unlimited quota, snapshot usage, null cache skips, and large-bucket-count behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/BucketUtilizationMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/DeleteKeysResult.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/DeleteKeysResult.java

## Purpose

`DeleteKeysResult` is a small result holder used by `DirectoryDeletingService`-related flows to return keys selected for deletion and whether keys were processed.

## Important APIs and Types

- Constructor accepts `List<OmKeyInfo> keysToDelete` and `boolean processedKeys`.
- `getKeysToDelete()` returns the key list.
- `isProcessedKeys()` returns the processing flag.

## Control Flow

There is no behavior beyond construction and getters.

## State and Persistence

The object holds in-memory result state only. It does not persist data; downstream deletion services decide how to move/purge OM metadata.

## Dependencies and Integration Points

It depends on `OmKeyInfo` and is referenced by `DirectoryDeletingService` and `KeyManager` methods for pending deletion subdirectories/subfiles.

## Risks and Edge Cases

The fields are mutable and not final, though there are no setters. The key list is returned directly, so callers can mutate it. The meaning of `processedKeys` requires external contract knowledge.

## Test Signals

Tests are likely indirect through directory deletion service behavior; direct tests would assert constructor/getter values and caller handling of empty lists or false processing state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/DeleteKeysResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/DeletingServiceMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/DeletingServiceMetrics.java

## Purpose

`DeletingServiceMetrics` registers and updates Hadoop metrics for OM key and directory deletion background services.

## Important APIs and Types

- `create()` registers the metrics source; `unregister()` removes it.
- Increment/update methods cover directory deletion totals, key deletion totals, purge counts, moved subfiles/subdirectories, last-run timestamps, AOS/snapshot last-run metrics, interval reclaimed metrics, and last AOS purge transaction info.
- `getLastAOSTransactionInfo` and `setLastAOSTransactionInfo` manage a monotonic `TransactionInfo`.
- `resetDirectoryMetrics` is visible for tests.

## Control Flow

Most methods directly increment or set `MutableGaugeLong` fields. Interval metrics call `checkAndResetMetrics`, which initializes `metricsResetTimeStamp` on first use and resets reclaimed keys/size if more than one day has elapsed. `setLastAOSTransactionInfo` synchronizes, compares the new transaction with the current one, and only updates gauges if it advances.

## State and Persistence

All state is process-local metrics gauge state registered in `DefaultMetricsSystem`. It resets on OM restart. The last AOS purge transaction metrics are used by deletion services to avoid starting a subsequent background run before the previous purge has been flushed, but they are metrics-backed process state rather than durable metadata.

## Dependencies and Integration Points

It integrates with Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MetricsRegistry`, `MutableGaugeLong`, `TransactionInfo`, and OM background services such as key deleting and directory deleting services.

## Risks and Edge Cases

Metrics fields are injected/initialized by the metrics system; direct construction outside `create()` can leave gauges null. Most updates are not synchronized, while transaction update is synchronized. The 24-hour reset is based on epoch seconds and only happens when interval metrics are updated. Gauges are used for cumulative counters, which is common in metrics2 but can surprise readers expecting counters.

## Test Signals

Tests should cover registration/unregistration, increment methods, interval reset behavior, monotonic transaction update, resetDirectoryMetrics, and service code updating last-run metrics with correct AOS/snapshot separation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/DeletingServiceMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/GrpcOzoneManagerServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/GrpcOzoneManagerServer.java

## Purpose

`GrpcOzoneManagerServer` is a separate Netty/gRPC network server for the OM gRPC transport used by S3 Gateway to OM communication.

## Important APIs and Types

- Constructor resolves max inbound response size, HA-specific or default gRPC port, creates gRPC metrics, and calls `init`.
- `init` builds thread pools/event loops, constructs a `NettyServerBuilder`, adds OM service and interceptors, installs metrics transport filters, and optionally configures TLS.
- `start`, `stop`, and `getPort` control the server lifecycle.

## Control Flow

Construction reads `OZONE_OM_GRPC_MAXIMUM_RESPONSE_LENGTH`, tries HA-suffixed `OZONE_OM_GRPC_PORT_KEY` using service ID and node ID, falls back to `GrpcOmTransportConfig`, creates metrics, then initializes the server. Initialization reads read-thread, boss-group, and worker-group sizes, creates daemon thread factories, creates `NioEventLoopGroup`s, builds a Netty server for the selected port with inbound size limit and executor, wraps `OzoneManagerServiceGrpc` with client-address and request/response metrics interceptors, and adds a metrics transport filter. If security and gRPC TLS are enabled, it builds a server SSL context from the certificate client's key manager, configured TLS provider, protocols, and ciphers; failures are logged but do not prevent building a non-TLS server.

`start` starts the server and updates `port` from the bound port. `stop` shuts down read executors, waits for gRPC shutdown, gracefully shuts down boss and worker event loops, logs, and always unregisters metrics.

## State and Persistence

The class holds process-local network server state: port, max size, metrics source, executor, event loop groups, and gRPC `Server`. It does not persist data.

## Dependencies and Integration Points

It integrates with OM protocol translator, `OzoneManagerServiceGrpc`, delegation token secret manager, certificate client/TLS config, gRPC Netty, Netty NIO event loops, gRPC metrics interceptors/filters, OM HA config suffixes, and `GrpcOmTransport` config.

## Risks and Edge Cases

TLS setup exceptions are logged but the server still starts without TLS if builder creation continues, which may be risky when TLS is expected. `stop` assumes all lifecycle fields are initialized and may throw unchecked exceptions if called after partial construction failure. Interrupted shutdown logs but does not re-interrupt the thread. The executor uses an unbounded queue, so slow request handling can accumulate memory pressure.

## Test Signals

Tests should cover HA and non-HA port resolution, start on port 0, interceptor/metrics registration, TLS enabled/disabled paths, graceful stop, and failure behavior when certificate/TLS setup fails.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/GrpcOzoneManagerServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/IOzoneAcl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/IOzoneAcl.java

## Purpose

`IOzoneAcl` is the common OM interface for retrieving ACLs and checking access on Ozone objects.

## Important APIs and Types

- `getAcl(OzoneObj obj)` returns `List<OzoneAcl>` and may throw `IOException`.
- `checkAccess(OzoneObj ozObject, RequestContext context)` returns whether the request context has access and may throw `OMException`.

## Control Flow

This is an interface; concrete behavior is implemented by managers such as `BucketManagerImpl` and key/volume managers.

## State and Persistence

The interface holds no state. Implementations usually read persisted OM metadata ACL lists.

## Dependencies and Integration Points

It depends on `OzoneAcl`, `OzoneObj`, `RequestContext`, and `OMException`. It is the shared ACL contract for OM managers.

## Risks and Edge Cases

Implementations must consistently handle object resource types, bucket links, missing metadata, and exception types. Mismatched semantics can lead to authorization inconsistencies.

## Test Signals

Contract tests should exercise positive/negative access checks, invalid object types, missing resources, and exception mapping for each implementing manager.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/IOzoneAcl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/KeyManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/KeyManager.java

## Purpose

`KeyManager` defines the OM key-level service contract. It extends filesystem-style OM operations through `OzoneManagerFS` and ACL behavior through `IOzoneAcl`.

## Important APIs and Types

The interface covers lifecycle (`start`, `stop`), key lookup/info/listing (`lookupKey`, `getKeyInfo`, `listKeys`), pending deletion queues (`getPendingDeletionKeys`, `getDeletedKeyEntries`, `getDeletedDirEntries`, `getPendingDeletionSubDirs`, `getPendingDeletionSubFiles`), snapshot rename/deletion lookups, previous-snapshot object lookup functions, multipart upload listing and cleanup selection, object tagging, block-location refresh, metadata manager access, and access to background services such as key deleting, directory deleting, open-key cleanup, multipart cleanup, SST filtering, snapshot defrag/deleting, and compaction.

## Control Flow

This file is an interface, so it defines contracts rather than implementation. The default `getDeletedDirEntries()` delegates to `getDeletedDirEntries(null, null)`. The default `getDeletedDirEntries(volume, bucket, size)` opens an iterator, copies up to `size` key/value pairs into a list using `Table.newKeyValue`, closes the iterator with try-with-resources, and returns the list.

## State and Persistence

The interface describes access to OM metadata tables for keys, open keys, deleted keys, deleted directories, multipart uploads, snapshot metadata, and rename entries. Implementations persist and read state through `OMMetadataManager` and related RocksDB-backed tables. Background services exposed by the interface mutate deletion and cleanup state over time.

## Dependencies and Integration Points

It integrates with OM helpers (`OmKeyInfo`, `OmKeyArgs`, `OmBucketInfo`, `OmDirectoryInfo`, multipart list types, `BucketLayout`, `RepeatedOmKeyInfo`), database abstractions (`Table`, `TableIterator`), Ratis/checked functions, Ozone Manager filesystem interface, background service classes, snapshot services, compaction service, and protobuf `ExpiredMultipartUploadsBucket`.

## Risks and Edge Cases

The contract is broad and central, so implementation consistency is critical. Pagination and filtering behavior for deletion queues must avoid starvation. Snapshot previous-object lookup functions return deferred `CheckedFunction<KeyManager,...>` values, which require careful lifecycle and snapshot table handling by callers. Cleanup service getters expose internal background services, so null/lifecycle handling matters during OM startup/shutdown. The default iterator-copy helper returns direct value objects and relies on iterator implementations for ordering and isolation.

## Test Signals

Strong coverage comes from key manager implementation tests for lookup/listing, block refresh, tags, multipart listing/expiration, open key cleanup, deleted key and deleted directory iteration, snapshot-aware deletion/rename logic, background service lifecycle, and ACL behavior inherited from `IOzoneAcl`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/KeyManager.java -->
