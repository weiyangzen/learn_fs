# subset-b-007416 research

Grouped research for Hadoop registry ZooKeeper, service-record type, DNS server, integration, and embedded-service sources. Each section preserves the source path and is intended to be split into the mapped source-tree-aligned research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/CuratorService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/CuratorService.java

## Purpose
`CuratorService` is the low-level Hadoop service wrapper around Apache Curator and ZooKeeper. It does not expose the public registry API directly; it supplies lifecycle-managed Curator access, registry-root path resolution, ZooKeeper CRUD helpers, ACL-aware creation, path watching, and diagnostics for higher-level services such as `RegistryOperationsService` and `RegistryDNSServer`.

## Important APIs and types
The class extends `CompositeService` and implements `RegistryConstants` plus `RegistryBindingSource`. Key fields are `CuratorFramework curator`, `registryRoot`, `RegistrySecurity registrySecurity`, `EnsembleProvider ensembleProvider`, and `CuratorCacheBridge curatorCacheBridge`. Lifecycle methods `serviceInit`, `serviceStart`, and `serviceStop` initialize security, build and start Curator, and close Curator/cache resources. Registry helpers include `zkStat`, `zkGetACLS`, `zkPathExists`, `zkMkPath`, `zkCreate`, `zkUpdate`, `zkSet`, `zkDelete`, `zkList`, `zkRead`, `dumpPath`, `registerPathListener`, `instantiateCacheForRegistry`, and `startCache`.

## Control flow
Initialization reads `KEY_REGISTRY_ZK_ROOT`, adds the `RegistrySecurity` child service, and defers Curator construction until start. `createCurator()` builds a binding from `RegistryBindingSource`, reads timeout/retry options, applies security under a class-level synchronized block because ZooKeeper security state is JVM-wide, then starts Curator. All ZooKeeper operations call `checkServiceLive()`, convert logical registry paths with `createFullPath()`, call Curator, and route failures through `operationFailure()`, which maps Keeper exceptions to Hadoop registry/filesystem exceptions.

## State and persistence behavior
The persistent state is ZooKeeper znodes below the configured registry root. `zkMkPath` and `zkCreate` create persistent or caller-supplied mode nodes with explicit ACLs; `zkSet` is create-or-update and treats overwrite flags at the caller boundary; `zkDelete` can delete recursively and may run in background when passed a callback. The service itself owns only transient Curator connection state and an optional cache watching the registry root.

## Dependencies and integration points
It integrates Curator, ZooKeeper `CreateMode`/`ACL`/`Stat`, Hadoop service lifecycle, `RegistrySecurity`, `RegistryPathUtils`, and registry exception classes. `RegistryOperationsService` uses the CRUD wrappers to implement the public API. `RegistryDNSServer` uses `instantiateCacheForRegistry` and `registerPathListener` to turn Curator cache events into DNS updates. `MicroZookeeperService` can provide its binding information through the same `RegistryBindingSource` abstraction.

## Risks and test signals
The create-if-absent flow is documented as check-then-create and is therefore race-prone when multiple clients create the same path; callers must tolerate `NodeExistsException` mapping. ACL lists are rejected when empty for `zkMkPath`, so tests should cover secure and insecure ACL creation. Path-listener callbacks convert `IOException` to `UncheckedIOException`, which can affect Curator listener threads. The file as read contains suspicious syntax duplication around `isSecure()` and should be covered by compilation. Behavioral tests should use an in-process ZooKeeper, verify exception translation, recursive delete, overwrite semantics, cache listener add/delete events, and SASL/digest configuration diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/CuratorService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/PathListener.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/PathListener.java

## Purpose
`PathListener` is a tiny callback interface for components interested in registry path changes detected through the Curator cache.

## Important APIs and types
It declares `nodeAdded(String path)` and `nodeRemoved(String path)`, both throwing `IOException`. Paths passed by `CuratorService.registerPathListener()` are absolute ZooKeeper paths from Curator event data, not necessarily registry-root-relative paths.

## Control flow
Implementations are invoked from Curator cache create/change and delete callbacks. The main implementation in this subset is the anonymous listener in `RegistryDNSServer.manageRegistryDNS()`, which resolves new records and removes DNS records when znodes disappear.

## State and persistence behavior
The interface has no state. Its persistence effect depends entirely on implementations; in `RegistryDNSServer`, it causes DNS zone mutations based on ZooKeeper registry content.

## Dependencies and integration points
It depends only on `java.io.IOException`. It connects the ZooKeeper client layer to server-side consumers without coupling `CuratorService` to DNS or registry administration logic.

## Risks and test signals
Because callbacks can throw `IOException`, caller code must decide whether to swallow, wrap, or propagate failures. Tests should assert that listener implementers receive both create/update and delete events with expected path form, and that exceptions do not silently corrupt downstream caches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/PathListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistryBindingSource.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistryBindingSource.java

## Purpose
`RegistryBindingSource` abstracts where ZooKeeper connection binding information comes from. It lets clients use configuration-backed fixed quorums, embedded ZooKeeper services, or future dynamic providers.

## Important APIs and types
The single method `supplyBindingInformation()` returns `BindingInformation`, which carries an `EnsembleProvider` and textual description. `CuratorService` implements this interface by building a fixed Curator ensemble from `KEY_REGISTRY_ZK_QUORUM`, while `MicroZookeeperService` implements it after starting its local server.

## Control flow
`CuratorService.createEnsembleProvider()` invokes this method immediately before Curator construction. The returned provider becomes the source of Curator's ZooKeeper ensemble, and the description is copied into diagnostics.

## State and persistence behavior
The interface owns no state. Implementers may expose transient runtime state, such as an embedded server's chosen port, or static configuration state.

## Dependencies and integration points
It is a public evolving interface in the ZooKeeper implementation package. Its key integration point is Curator builder setup, and it allows a registry client and an embedded ZooKeeper service to be composed under one service lifecycle.

## Risks and test signals
Implementers must not return incomplete binding data. `MicroZookeeperService.supplyBindingInformation()` explicitly fails before the service has started. Tests should validate that `CuratorService` can consume both self-supplied fixed bindings and externally supplied bindings, and that diagnostics preserve the source description.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistryBindingSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistryInternalConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistryInternalConstants.java

## Purpose
`RegistryInternalConstants` centralizes implementation-only constants for registry path validation and ZooKeeper ACL/security wiring.

## Important APIs and types
The constants include `VALID_PATH_ENTRY_PATTERN`, permission masks for readers, system services, and user roots, `SASLAUTHENTICATION_PROVIDER`, `ZOOKEEPER_AUTH_PROVIDER`, and `HADOOP_USER_NAME`. Permission masks are defined using `ZooDefs.Perms`.

## Control flow
There are no functions. Consumers import these values when validating registry path components or configuring ZooKeeper server SASL support. `MicroZookeeperService.setupSecurity()` uses the auth-provider constants to install SASL ACL support into the embedded server.

## State and persistence behavior
No runtime state is stored. The constants affect persistent ZooKeeper ACLs when used to create nodes and affect JVM/server security properties when configuring SASL.

## Dependencies and integration points
The interface depends on ZooKeeper `ZooDefs`. It is internal to the `impl.zk` package and complements the public `RegistryConstants`.

## Risks and test signals
The path-entry regex allows unlimited segment length and lowercase alphanumeric/hyphen names only; tests should verify this matches registry path rules wherever enforced. ACL permission constants should be tested indirectly through secure registry node creation, especially user root permissions that intentionally omit ACL administration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistryInternalConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistryOperationsService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistryOperationsService.java

## Purpose
`RegistryOperationsService` implements the public `RegistryOperations` API on top of `CuratorService`. It is the bridge from logical registry operations and JSON service records to ZooKeeper znodes.

## Important APIs and types
The class extends `CuratorService` and implements `RegistryOperations`. Public operations are `mknode`, `bind`, `resolve`, `exists`, `stat`, `list`, and `delete`. It uses `RegistryUtils.ServiceRecordMarshal` for JSON bytes, `RegistryTypeUtils.validateServiceRecord` for validation, `BindFlags.OVERWRITE`, `RegistryPathStatus`, and client ACLs from `RegistrySecurity`.

## Control flow
`mknode` validates the path and calls `zkMkPath` with persistent mode and client ACLs. `bind` validates the path and record, marshals the `ServiceRecord`, and calls `zkSet` with overwrite controlled by flags. `resolve` reads bytes from ZooKeeper, unmarshals and validates the record. `stat` converts ZooKeeper `Stat` into a registry-facing `RegistryPathStatus` using last path entry, creation time, data length, and child count.

## State and persistence behavior
All persistence is ZooKeeper znode persistence below the registry root. Bound records are persistent znodes containing marshalled JSON. The service does not add application-level version checks around updates, so last writer wins when overwrite is enabled.

## Dependencies and integration points
It depends on `CuratorService`, registry API interfaces, bind flags, registry path/type utilities, ZooKeeper `CreateMode` and `Stat`, and ACLs from `RegistrySecurity`. It is used directly by registry clients and by `RegistryDNSServer` for watching and resolving records.

## Risks and test signals
`validatePath` currently performs no checks, so path correctness depends on lower-level utilities and ZooKeeper. `bind` validates before writing, so tests should include invalid service record rejection, overwrite/no-overwrite behavior, resolve round trips, stat field mapping, and ACL behavior in secure mode. Race behavior in inherited `zkSet` should be tested with concurrent binders if correctness matters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistryOperationsService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistrySecurity.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistrySecurity.java

## Purpose
`RegistrySecurity` owns registry security policy: reading auth configuration, building ZooKeeper ACLs, setting Curator auth, creating JAAS/SASL client settings, digest helpers, and diagnostics. It is intentionally a Hadoop service so tests and parent services can initialize it independently.

## Important APIs and types
The class extends `AbstractService`. It defines internal `AccessPolicy` values `anon`, `sasl`, `digest`, and `simple`; static ACLs `ALL_READWRITE_ACCESS`, `ALL_READ_ACCESS`, and `WorldReadWriteACL`; ACL collections `systemACLs` and `digestACLs`; Kerberos/JAAS fields; and many helpers. Key methods are `serviceInit`, `initSecurity`, `getClientACLs`, `createSaslACLFromCurrentUser`, `createSaslACL`, `digest`, `toDigestId`, `splitAclPairs`, `parse`, `buildACLs`, `parseACLs`, `createJAASEntry`, `applySecurityEnvironment`, `setZKSaslClientProperties`, `clearZKSaslClientProperties`, `buildSecurityDiagnostics`, and `createACLfromUsername`.

## Control flow
`serviceInit` maps `KEY_REGISTRY_CLIENT_AUTH` to an access policy and calls `initSecurity()`. In secure mode it adds world-read access, derives a Kerberos realm, builds system ACLs from configured principals, builds user ACLs, optionally adds current Kerberos user ACLs, then configures SASL or digest credentials depending on access mode. In insecure mode it grants world read/write. `applySecurityEnvironment()` mutates the Curator builder and JVM ZooKeeper properties according to the selected access policy.

## State and persistence behavior
The persistent impact is ACLs placed on ZooKeeper nodes by callers using `getClientACLs()` or `getSystemACLs()`. Digest credentials are stored in memory as auth bytes for Curator. JAAS and ZooKeeper SASL settings are process-wide JVM state, so multiple clients with different security settings can interfere.

## Dependencies and integration points
It integrates Hadoop `UserGroupInformation`, Hadoop auth `JaasConfiguration` and `KerberosUtil`, Curator builder authorization, ZooKeeper ACL/Id/digest providers, `ZKUtil` ACL parsing, and registry constants. `CuratorService` delegates all security setup to it; `MicroZookeeperService` uses static helpers for server-side SASL context validation and system properties.

## Risks and test signals
Because it sets JVM-wide JAAS/ZooKeeper properties, tests must isolate or clear system properties. Digest ACL strings are partially obfuscated for logs, which should be verified to avoid leaking secrets. Secure SASL mode requires Hadoop security to be enabled or initialization fails. The file as read contains suspicious duplicated code/text in the SASL switch and JAAS template area, so compilation is a primary test signal. Behavioral coverage should include anonymous, simple, digest, and Kerberos paths; realm suffix handling; empty user ACL failure; malformed ACL parsing; and principal/keytab supplied versus pre-existing JAAS configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistrySecurity.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/ZKPathDumper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/ZKPathDumper.java

## Purpose
`ZKPathDumper` is a visible-for-testing diagnostics helper that lazily renders a ZooKeeper subtree to a string.

## Important APIs and types
The constructor accepts a `CuratorFramework`, root path, and verbose flag. `toString()` starts recursive expansion. Private `expand` lists children, checks each child's stat, optionally fetches ACLs, marks ephemeral nodes with `*`, and indents by `INDENT`.

## Control flow
The dump is only performed when `toString()` is evaluated, which makes it suitable for log statements. It performs depth-first traversal from the configured root and appends any exception text into the output rather than throwing.

## State and persistence behavior
It does not mutate ZooKeeper. It reads child lists, stats, and optionally ACLs from live ZooKeeper state. Output includes znode data lengths and ephemeral-owner status, not znode payload bytes.

## Dependencies and integration points
It depends on Curator child/stat/ACL APIs and `RegistrySecurity.aclToString`. `CuratorService.dumpPath()` and `dumpRegistryRobustly()` expose it for service diagnostics.

## Risks and test signals
Verbose ACL output appends ACL text before child path text in the current builder flow, so formatting should be checked. It swallows traversal exceptions into the dump, which is useful for diagnostics but can hide test failures unless tests assert content. Tests should cover nested paths, ephemeral marking, verbose ACL rendering, and missing/permission-denied paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/ZKPathDumper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/ZookeeperConfigOptions.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/ZookeeperConfigOptions.java

## Purpose
`ZookeeperConfigOptions` lists ZooKeeper client/server system-property names and auth scheme names used by the registry security code.

## Important APIs and types
Constants cover SASL client enablement, JAAS login context, SASL client username, server SASL context, failed-SASL downgrade behavior, server realm, kinit path, and ID schemes `sasl` and `digest`. Some values are sourced from ZooKeeper classes such as `ZKClientConfig.LOGIN_CONTEXT_NAME_KEY` and `ZooKeeperSaslServer.LOGIN_CONTEXT_NAME_KEY`.

## Control flow
There are no methods. `RegistrySecurity` reads and writes these JVM properties for client-side auth. `MicroZookeeperService` uses the server-side context and failed-SASL settings when booting an embedded secure ZooKeeper.

## State and persistence behavior
The constants themselves are stateless, but they name JVM-wide system properties. Changes affect all ZooKeeper clients and servers in the same process.

## Dependencies and integration points
It depends on ZooKeeper client/server config classes and is referenced by security and embedded service code. It is package-internal API for coordinating ZooKeeper security setup.

## Risks and test signals
The class comments correctly warn that only one independently configured ZooKeeper client/service can be safe in a JVM. Tests should set and clear the named properties around each case and verify SASL enable/disable behavior does not leak across test methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/ZookeeperConfigOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/package-info.java

## Purpose
This package descriptor documents the registry's core ZooKeeper support package.

## Important APIs and types
It points readers to `CuratorService` for service-managed Curator access, `RegistrySecurity` for ACL and security setup, and `ZookeeperConfigOptions` for ZooKeeper system-property definitions.

## Control flow
There is no executable code. It describes the package organization and the requirement that some ZooKeeper system properties be set before object construction or operation invocation.

## State and persistence behavior
No state is stored here. The described package persists registry entries in ZooKeeper and uses JVM-wide security state.

## Dependencies and integration points
The package integrates the public registry operations with Apache Curator/ZooKeeper and Hadoop service lifecycle. It is consumed by higher-level client operations and server-side DNS/admin services.

## Risks and test signals
The package-level warning about system properties is a key test design signal: secure ZooKeeper tests must avoid sharing conflicting clients in the same JVM or must reset properties aggressively.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/AddressTypes.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/AddressTypes.java

## Purpose
`AddressTypes` defines string constants for endpoint address encodings used in JSON service records. Strings are used instead of Java enums for cross-language serialization compatibility.

## Important APIs and types
Important address type constants are `ADDRESS_HOSTNAME_AND_PORT`, `ADDRESS_PATH`, `ADDRESS_URI`, `ADDRESS_ZOOKEEPER`, and `ADDRESS_OTHER`. Field names include `ADDRESS_HOSTNAME_FIELD` and `ADDRESS_PORT_FIELD`.

## Control flow
There is no control flow. Constructors and processors in `Endpoint`, `RegistryTypeUtils`, and DNS service-record processors interpret these strings.

## State and persistence behavior
Values become persisted JSON fields in `Endpoint.addressType` and keys in endpoint address maps. They form part of the external registry data contract.

## Dependencies and integration points
`Endpoint` uses these constants when constructing URI endpoints. `BaseServiceRecordProcessor` interprets `host/port` and `uri` endpoints to extract host, port, and TXT path values. Clients publishing service records must use the same names.

## Risks and test signals
Because address payloads are maps of strings, malformed or missing keys fail later in processors rather than at deserialization. Tests should cover all standard address types, especially DNS extraction from `host/port` and `uri`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/AddressTypes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/Endpoint.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/Endpoint.java

## Purpose
`Endpoint` is the JSON-marshallable description of one service or component API endpoint. It records the API identifier, address encoding, protocol, and one or more address maps.

## Important APIs and types
Public fields are `api`, `addressType`, `protocolType`, and `addresses`. Constructors support empty creation for Jackson, deep-copy construction, explicit address lists, a single address map, varargs address maps, and URI varargs. `validate()` checks required fields and non-null address entries. `toString()` delegates to a static `JsonSerDeser<Endpoint>` marshal.

## Control flow
The deep-copy constructor clones the address list and maps. URI construction sets `addressType` to `AddressTypes.ADDRESS_URI` and creates address maps through `RegistryTypeUtils.uri`. `validate()` is called by `ServiceRecord.addExternalEndpoint`, `addInternalEndpoint`, and higher-level service-record validation before persistence.

## State and persistence behavior
Instances are mutable DTOs intended for JSON persistence inside `ServiceRecord`. The copy constructor is deep for addresses, while `clone()` is explicitly shallow and shares address list objects.

## Dependencies and integration points
It depends on Jackson annotations, Hadoop `Preconditions`, `JsonSerDeser`, `RegistryTypeUtils`, `AddressTypes`, and `ProtocolTypes`. DNS processors consume endpoint address maps to generate A, AAAA, CNAME, SRV, and TXT records.

## Risks and test signals
The public mutable fields are convenient for JSON but can be changed after validation. `clone()` is shallow while the copy constructor is deep, so tests should distinguish them. DNS code assumes at least one address and specific keys for selected address types; endpoint validation does not enforce address schema by type, so schema-specific tests belong in registry type utilities and DNS processors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/Endpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/ProtocolTypes.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/ProtocolTypes.java

## Purpose
`ProtocolTypes` defines common protocol strings for endpoint metadata in service records.

## Important APIs and types
Constants include Hadoop filesystem, Hadoop IPC, IIOP, REST, RMI, Sun RPC, Thrift, TCP, UDP, unknown, web UI, web services, and ZooKeeper binding protocol names.

## Control flow
There are no methods. Values are assigned to `Endpoint.protocolType` by publishers and interpreted by clients according to application conventions.

## State and persistence behavior
Protocol strings are persisted as JSON and form part of the registry service-record contract. Unknown or custom values are represented by strings, with `PROTOCOL_UNKNOWN` as the empty string.

## Dependencies and integration points
It integrates with `Endpoint`, `ServiceRecord`, and client code that resolves endpoint protocol choices. DNS code in this subset focuses more on address type and API name than protocol type.

## Risks and test signals
Because protocols are plain strings, registry validation must allow custom protocols while still rejecting null fields. Tests should verify standard constants survive JSON round trips and that unknown protocols are accepted where the data model promises extensibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/ProtocolTypes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/RegistryPathStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/RegistryPathStatus.java

## Purpose
`RegistryPathStatus` is the JSON-friendly result of a registry `stat()` call. It summarizes one registry entry's name, timestamp, data size, and child count.

## Important APIs and types
The final fields are `path`, `time`, `size`, and `children`, populated through a Jackson `@JsonProperty` constructor. `equals()` compares path, time, and size but intentionally ignores `children`; `hashCode()` derives only from path.

## Control flow
Instances are created by `RegistryOperationsService.stat()` from ZooKeeper `Stat`, using the last path entry as `path`, creation time as `time`, data length as `size`, and number of children as `children`.

## State and persistence behavior
This class is not stored in the registry as service data; it is a status DTO that can be serialized for APIs or REST front ends. It reflects ZooKeeper metadata at one point in time.

## Dependencies and integration points
It uses Jackson annotations and Hadoop audience/stability annotations. It is consumed by registry listing/extraction utilities and by `SelectByYarnPersistence` selectors, though selectors in this subset do not inspect its fields.

## Risks and test signals
Ignoring `children` in equality but including it in `toString()` is intentional but can surprise caches or comparisons. Tests should assert JSON construction, equality semantics, and `RegistryOperationsService.stat()` mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/RegistryPathStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/ServiceRecord.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/ServiceRecord.java

## Purpose
`ServiceRecord` is the primary JSON-marshallable registry value describing a service/component, its attributes, and internal/external endpoints.

## Important APIs and types
Public fields are `type`, `description`, `external`, and `internal`; unknown JSON attributes are stored in private `attributes`. `RECORD_TYPE` identifies valid registry records. Methods add and retrieve endpoints, set and get attributes with Jackson `@JsonAnySetter`/`@JsonAnyGetter`, find endpoints by API, render to string, and implement equality/hashCode. The copy constructor deep-copies attributes and endpoints.

## Control flow
Publishers populate attributes and endpoints, `addExternalEndpoint`/`addInternalEndpoint` validate endpoints immediately, and `RegistryOperationsService.bind()` invokes registry-wide validation before marshalling. DNS processors read YARN attributes and endpoint lists to generate records.

## State and persistence behavior
Instances are mutable DTOs stored as JSON bytes in ZooKeeper. Unknown JSON fields are retained in `attributes` and emitted through `@JsonAnyGetter`; the class comments say generated JSON does not include creation of unknown attributes, but the getter exposes the map during serialization.

## Dependencies and integration points
It depends on Jackson any-getter/setter support, Hadoop `Preconditions`, and `Endpoint`. YARN-specific constants in `YarnRegistryAttributes` define expected attribute keys. `RegistryUtils.ServiceRecordMarshal` serializes/deserializes it, and DNS processors require `yarn:persistence`, `yarn:ip`, `yarn:hostname`, `yarn:id`, and component data.

## Risks and test signals
`findByAPI` assumes endpoints are non-null and have non-null APIs. `set(String,Object)` calls `toString()` on values, so null unknown attributes would fail. `clone()` is shallow despite a deep-copy constructor. Tests should cover JSON round trips, unknown attribute preservation, endpoint validation, equality including endpoints/attributes, and DNS behavior for missing YARN attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/ServiceRecord.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/package-info.java

## Purpose
This package descriptor documents the JSON data model saved to or derived from the registry.

## Important APIs and types
It identifies `ServiceRecord` and `Endpoint` as the core persisted data types and `AddressTypes`, `PersistencePolicies`, and `ProtocolTypes` as supporting field-value contracts. It also explains that `RegistryPathStatus` is a status object, not a saved service record.

## Control flow
There is no executable control flow. The descriptor guides how clients should view the package boundary.

## State and persistence behavior
The package's data types are designed for JSON marshalling into ZooKeeper registry entries. `RegistryPathStatus` is transient metadata that can still be serialized.

## Dependencies and integration points
These types are consumed by registry clients, YARN publishers, registry admin cleanup selectors, and DNS record processors.

## Risks and test signals
Package-level docs signal that cross-language JSON compatibility is a design goal. Tests should favor stable field names and string constants over Java-only enum assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/yarn/PersistencePolicies.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/yarn/PersistencePolicies.java

## Purpose
`PersistencePolicies` defines YARN-specific lifecycle strings for service records.

## Important APIs and types
Constants are `PERMANENT`, `APPLICATION`, `APPLICATION_ATTEMPT`, and `CONTAINER`. They are intended for the `yarn:persistence` attribute in `ServiceRecord`.

## Control flow
No methods are present. Runtime consumers compare service-record attributes with these policy strings or equivalent literals.

## State and persistence behavior
The policy value is persisted as a string attribute in service records. Server cleanup and DNS code use it to decide whether a record describes an application-level service or a container-level endpoint.

## Dependencies and integration points
It references `ServiceRecord` in documentation. `SelectByYarnPersistence` selects records by policy, and `RegistryDNS` treats the literal `container` as the container DNS path.

## Risks and test signals
Because policies are not enums, typoed values become silent non-matches. Tests should verify that cleanup selectors and DNS registration use the same policy string values as publishers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/yarn/PersistencePolicies.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/yarn/YarnRegistryAttributes.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/yarn/YarnRegistryAttributes.java

## Purpose
`YarnRegistryAttributes` defines YARN-specific attribute keys used inside `ServiceRecord.attributes`.

## Important APIs and types
The class is final with a hidden constructor. Constants include `YARN_ID`, `YARN_PERSISTENCE`, `YARN_PATH`, `YARN_HOSTNAME`, `YARN_IP`, and `YARN_COMPONENT`.

## Control flow
There are no methods. Consumers call `ServiceRecord.get()` with these keys.

## State and persistence behavior
These keys are persisted as JSON attributes on service records. DNS processors use them to generate container names, reverse records, and persistence-category routing. Cleanup selectors use ID and persistence for record selection.

## Dependencies and integration points
The class is used by `RegistryDNS`, `ContainerServiceRecordProcessor`, `SelectByYarnPersistence`, and any YARN publisher or cleaner interacting with the registry.

## Risks and test signals
Missing attributes can cause processors to skip records, log warnings, or throw runtime exceptions. Tests should cover complete and incomplete YARN records, especially `yarn:ip`, `yarn:hostname`, `yarn:id`, `yarn:component`, and `yarn:persistence`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/yarn/YarnRegistryAttributes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/conf/RegistryConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/conf/RegistryConfiguration.java

## Purpose
`RegistryConfiguration` is a thin `Configuration` subclass that imports YARN default and site resources for registry users.

## Important APIs and types
The static initializer calls `Configuration.addDefaultResource("yarn-default.xml")` and `Configuration.addDefaultResource("yarn-site.xml")`. The constructor delegates to `super()`.

## Control flow
Class loading registers the YARN resource files globally with Hadoop configuration defaults. Creating a `RegistryConfiguration` then sees registry/YARN keys from those resources.

## State and persistence behavior
No registry data is persisted. The static default-resource registration is process-level configuration state.

## Dependencies and integration points
`RegistryDNSServer.main()` and `PrivilegedRegistryDNSStarter` use this class to parse command-line and site configuration before launching DNS services. It exists because registry configuration keys historically live in YARN configuration files.

## Risks and test signals
Static default-resource registration can affect other `Configuration` instances in the same JVM. Tests should confirm expected keys load from YARN resources and isolate global configuration effects where needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/conf/RegistryConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/conf/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/conf/package-info.java

## Purpose
This package descriptor identifies the configuration package for the Hadoop Service Registry.

## Important APIs and types
The package's direct class in this subset is `RegistryConfiguration`, which imports YARN resources.

## Control flow
No executable code is present.

## State and persistence behavior
The package deals with Hadoop configuration state, not registry persistence.

## Dependencies and integration points
Configuration objects from this package are used by registry services and DNS launchers to obtain registry, ZooKeeper, DNS, and security settings.

## Risks and test signals
Tests should treat configuration resource loading as part of service bootstrap, especially when DNS and ZooKeeper default keys come from YARN XML files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/conf/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ApplicationServiceRecordProcessor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ApplicationServiceRecordProcessor.java

## Purpose
`ApplicationServiceRecordProcessor` converts application-level `ServiceRecord` instances into DNS record descriptors for A, AAAA, CNAME, SRV, and TXT records.

## Important APIs and types
It extends `BaseServiceRecordProcessor`. `initTypeToInfoMapping()` iterates record types and creates descriptor lists. Nested descriptors include `TXTApplicationRecordDescriptor`, `SRVApplicationRecordDescriptor`, `CNAMEApplicationRecordDescriptor`, `AApplicationRecordDescriptor`, and `AAAAApplicationRecordDescriptor`.

## Control flow
If no external endpoints exist, processing logs and returns without registering descriptors. For each external endpoint, TXT/SRV/CNAME descriptors are created. The A descriptor uses the first external endpoint host as the application address. The AAAA descriptor subclasses A and maps the resolved IPv4 address into an IPv6-mapped address.

## State and persistence behavior
No source registry state is changed. Descriptor output is later consumed by `manageDNSRecords()` to mutate in-memory DNS zones through `RegistryDNS.RegistryCommand`.

## Dependencies and integration points
It depends on `Endpoint`, `ServiceRecord`, xbill `Name`/`Type`, and helper methods in `BaseServiceRecordProcessor` for service names, endpoint names, host/port extraction, TXT text, and IPv6 mapping. `RegistryDNS.op()` chooses this processor for non-container records with YARN persistence.

## Risks and test signals
The code assumes external endpoints have at least one address and resolvable hosts. API-name shortening asserts non-null support for either YARN service API prefixes or HTTP APIs. Tests should cover empty external endpoints, URI and host/port endpoints, multiple endpoints generating API records, invalid host/port values, and generated record names under user/service domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ApplicationServiceRecordProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/BaseServiceRecordProcessor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/BaseServiceRecordProcessor.java

## Purpose
`BaseServiceRecordProcessor` provides common DNS descriptor machinery for translating registry `ServiceRecord` data into xbill DNS records.

## Important APIs and types
It implements `ServiceRecordProcessor`. Core state includes `ZoneSelector zoneSelctor`, `typeToDescriptorMap`, `path`, and `domain`. Important methods are `getIpv6Address`, `reverseIP`, `manageDNSRecords`, `registerRecordDescriptor`, and path getters/setters. Nested abstract descriptors are `RecordDescriptor<T>`, `ContainerRecordDescriptor<T>`, and `ApplicationRecordDescriptor<T>`.

## Control flow
Subclasses initialize `typeToDescriptorMap` with record-type-specific descriptors. `manageDNSRecords()` walks type-to-descriptor entries, asks `RecordCreatorFactory` for the correct creator, creates concrete records for every descriptor name, and executes the registry command against the best zone selected by `ZoneSelector`.

## State and persistence behavior
The class stores transient descriptor state. Zone mutations are deferred to caller-provided commands. No ZooKeeper writes occur here.

## Dependencies and integration points
It depends on registry path utilities, `AddressTypes`, `Endpoint`, `ServiceRecord`, xbill `Name` and `ReverseMap`, Java networking, URI parsing, and `ZoneSelector`. `ApplicationServiceRecordProcessor` and `ContainerServiceRecordProcessor` subclass it.

## Risks and test signals
`zoneSelctor` is misspelled but functional. Endpoint helpers assume the first address entry is present and valid. `getDNSApiFragment` uses an `assert` for unsupported API forms, which may be disabled in production. Tests should cover DNS name construction from registry paths, IPv4-to-IPv6 mapping, reverse IP mapping, unsupported endpoint/API formats, and that `manageDNSRecords()` invokes commands with matching zones and record types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/BaseServiceRecordProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ContainerServiceRecordProcessor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ContainerServiceRecordProcessor.java

## Purpose
`ContainerServiceRecordProcessor` converts container-level YARN `ServiceRecord` instances into A, AAAA, PTR, and TXT DNS descriptors.

## Important APIs and types
It extends `BaseServiceRecordProcessor`. Nested descriptors are `TXTContainerRecordDescriptor`, `PTRContainerRecordDescriptor`, `AContainerRecordDescriptor`, and `AAAAContainerRecordDescriptor`. It reads `YarnRegistryAttributes.YARN_IP`, `YARN_HOSTNAME`, `YARN_ID`, and `YARN_COMPONENT`.

## Control flow
`initTypeToInfoMapping()` only proceeds when `yarn:ip` exists. A records target the parsed IP and use names based on container name, container ID, and component name. AAAA records map the same IPv4 address into IPv6. PTR records use reverse IP names when both host and IP exist and point to the container DNS name. TXT records attach the YARN ID to the container name.

## State and persistence behavior
The processor produces transient descriptors that are later registered or removed from in-memory DNS zones. It does not persist to ZooKeeper.

## Dependencies and integration points
It depends on YARN service-record attributes, registry path parsing in the base class, xbill DNS types, and Java networking. `RegistryDNS` chooses it when `yarn:persistence` equals `container`.

## Risks and test signals
Several descriptor init methods catch parse exceptions with TODO-style comments and may leave null names, which can later fail during record creation or zone selection. Missing `yarn:ip` silently produces no descriptors. Tests should cover full container records, missing host/IP/component/description cases, PTR generation, null-name behavior, and record removal symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ContainerServiceRecordProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/LookupTask.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/LookupTask.java

## Purpose
`LookupTask` wraps an xbill DNS lookup in a `Callable<Record[]>` so remote lookup can run with a timeout.

## Important APIs and types
The constructor stores a `Name` and integer DNS `type`. `call()` returns `new Lookup(name, type).run()`.

## Control flow
`RegistryDNS.getRecords()` creates a single-thread executor, submits `LookupTask`, and waits up to 1500 ms. This isolates potentially blocking upstream DNS calls from the main response path.

## State and persistence behavior
The task is stateless after construction and does not persist data. It reads from globally configured xbill DNS resolver state.

## Dependencies and integration points
It depends on xbill `Lookup`, `Name`, and `Record`, and is only used by `RegistryDNS` remote lookup fallback.

## Risks and test signals
Since `Lookup` uses global resolver configuration, tests should set resolver state deterministically. Timeout and exception behavior are controlled by `RegistryDNS.getRecords()`, not this class. Tests should verify that upstream lookup failures return null/empty responses without blocking DNS serving threads indefinitely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/LookupTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/PrivilegedRegistryDNSStarter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/PrivilegedRegistryDNSStarter.java

## Purpose
`PrivilegedRegistryDNSStarter` is an Apache Commons Daemon entry point that lets Registry DNS bind a privileged port before dropping into normal service launch.

## Important APIs and types
It implements `Daemon` with `init`, `start`, `stop`, and `destroy`. State includes `Configuration conf`, `RegistryDNS registryDNS`, and `RegistryDNSServer registryDNSServer`.

## Control flow
`init()` parses daemon arguments into a `RegistryConfiguration`, validates that `KEY_DNS_PORT` is in the privileged range 1-1023, creates a `RegistryDNS`, and calls `initializeChannels(conf)` early. `start()` launches `RegistryDNSServer` with the pre-initialized `RegistryDNS`. `destroy()` stops the launched server.

## State and persistence behavior
It creates socket/channel state in `RegistryDNS` before full server startup. It does not persist registry data.

## Dependencies and integration points
It integrates Commons Daemon, `DNSOperationsFactory`, `RegistryConfiguration`, generic Hadoop options, registry DNS constants, and `RegistryDNSServer.launchDNSServer`.

## Risks and test signals
The port check rejects non-privileged ports, so this starter is not a general launcher. `stop()` is empty while `destroy()` stops the service, which may matter to daemon containers. Tests should validate privileged-port guard behavior, early channel initialization idempotence, and cleanup when `init()` partially fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/PrivilegedRegistryDNSStarter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/RecordCreatorFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/RecordCreatorFactory.java

## Purpose
`RecordCreatorFactory` maps DNS record type codes to small creator objects that build xbill DNS `Record` instances with the configured TTL.

## Important APIs and types
Static state is `ttl`, set by `setTtl(long)`. `getRecordCreator(int)` supports A, AAAA, CNAME, TXT, PTR, and SRV. Nested `RecordCreator<R,T>` defines `create(Name,T)`. Concrete creators build `ARecord`, `AAAARecord`, `CNAMERecord`, `TXTRecord`, `PTRRecord`, and `SRVRecord`. `HostPortInfo` carries SRV target host and port.

## Control flow
`BaseServiceRecordProcessor.manageDNSRecords()` selects a creator per record type, passes descriptor names and targets, and sends the created record to a registry command.

## State and persistence behavior
TTL is process-global static state for all records produced by this factory. Created records are in-memory objects until added to DNS zones by `RegistryDNS`.

## Dependencies and integration points
It depends on xbill DNS record classes and Java `InetAddress`. `RegistryDNS.initializeZones()` sets TTL from configuration before service records are processed.

## Risks and test signals
The static TTL can leak between tests or multiple service instances in one JVM. SRV priority and weight are hard-coded to 1. Tests should verify each supported type creation, unknown type rejection, TTL propagation, and SRV target/port behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/RecordCreatorFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/RegistryDNS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/RegistryDNS.java

## Purpose
`RegistryDNS` is the DNS service that reflects YARN registry service records into xbill DNS zones and answers UDP/TCP DNS queries. It implements `DNSOperations` for register/delete and `ZoneSelector` for processor zone lookup.

## Important APIs and types
The class extends `AbstractService`. Major state includes an executor, read/write zone lock, `domainName`, `ttl`, DNSSEC flag and key data, `dnsKeyRecs`, `zones`, `bindHost`, channel initialization flag, and resolver update state. Important methods include `initializeChannels`, `serviceInit`, `initializeZones`, reverse-zone helpers, `configureZone`, DNSSEC setup/signing, NIO TCP/UDP serving, `generateReply`, `addAnswer`, `remoteLookup`, `findExactMatch`, `findBestZone`, `register`, `delete`, and nested `RegistryCommand` implementations.

## Control flow
Service initialization updates default resolvers, reads the DNS domain, builds zones from files/configuration, creates primary and reverse zones, and opens UDP/TCP listeners. Query serving parses DNS messages, rejects unsupported opcodes/types, answers from local zones with authoritative data when possible, falls back to upstream lookup when local lookup fails, adds glue/additional records, and handles AXFR over TCP. Registry mutations route through `op()`, which selects a container or application service-record processor based on `yarn:persistence`, then executes add/remove commands for generated records.

## State and persistence behavior
The DNS zone map is in-memory service state. Records are added and removed dynamically as registry events arrive. DNSSEC keys are loaded from configuration/files and signatures are added to RRsets when enabled. Zone files can seed initial zones. No DNS state is written back to ZooKeeper by this class.

## Dependencies and integration points
It uses many xbill DNS classes, Hadoop `DNSOperations`, `ServiceRecord`, YARN attributes, Hadoop executor/thread helpers, `ReverseZoneUtils`, `SecureableZone`, `RecordCreatorFactory`, and service-record processors. It is launched by `RegistryDNSServer` or pre-initialized by `PrivilegedRegistryDNSStarter`.

## Risks and test signals
Concurrency centers on `ReentrantReadWriteLock`; add/remove paths should consistently hold write locks, but `removeRecordCommand` removes without the wrapper lock in the read source, so concurrent query/mutation tests are important. Remote lookup creates a new single-thread executor per lookup. DNSSEC code depends on key config and file format and the file as read contains suspicious duplicated method signature text in `enableDNSSECIfNecessary`; compilation is a critical signal. Query tests should cover UDP/TCP, EDNS DO flag, CNAME recursion, NXDOMAIN/NXRRSET, SOA/NS authority, reverse zones, split reverse zones, DNSSEC signing/NXT, AXFR, and service-record registration/delete symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/RegistryDNS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/RegistryDNSServer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/RegistryDNSServer.java

## Purpose
`RegistryDNSServer` composes registry ZooKeeper operations and `RegistryDNS` into a lifecycle-managed DNS server that reacts to registry path changes.

## Important APIs and types
It extends `CompositeService`. State includes `RegistryDNS registryDNS`, `RegistryOperationsService registryOperations`, and `ConcurrentMap<String, ServiceRecord> pathToRecordMap`. Key methods are `serviceInit`, `serviceStart`, `manageRegistryDNS`, `processServiceRecords`, `processServiceRecord`, `launchDNSServer`, and `main`.

## Control flow
Initialization creates a registry operations child and a DNS child, using `DNSOperationsFactory` if a DNS instance was not injected. Start calls `manageRegistryDNS()`, which instantiates a Curator cache, registers a `PathListener`, starts the cache, and maps node additions to record extraction and DNS registration. Node removals look up the prior record in `pathToRecordMap` and delete generated DNS records.

## State and persistence behavior
The server reads persistent ZooKeeper service records via `RegistryOperationsService`. It maintains a transient map from relative registry path to the last seen `ServiceRecord` so delete events have enough data to remove DNS records. DNS state remains in the `RegistryDNS` in-memory zones.

## Dependencies and integration points
It integrates Curator path listening, registry path utilities, `RegistryUtils.extractServiceRecords`, `RegistryDNS`, Hadoop service launch/shutdown utilities, `RegistryConfiguration`, and generic options parsing.

## Risks and test signals
Path normalization is central: add events process relative paths but delete events use `path.substring(registryRoot.length())` to look up cached records. Tests should verify add/delete path keys match. If listener setup fails, DNS support is disabled with a warning but the service remains started. Tests should cover initial cache events, updates, deletes, malformed service records, injected DNS instances, shutdown hooks, and command-line launch failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/RegistryDNSServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ReverseZoneUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ReverseZoneUtils.java

## Purpose
`ReverseZoneUtils` provides helper calculations for DNS reverse-zone setup, especially when splitting a subnet into multiple reverse zones.

## Important APIs and types
Key methods are `getReverseZoneNetworkAddress(String,int,int)`, `getSubnetCountForReverseZones(Configuration)`, private `calculateIp`, and visible-for-testing `splitIp`. Constants `POW3`, `POW2`, and `POW1` convert IPv4 octets to numeric offsets.

## Control flow
`getSubnetCountForReverseZones` reads subnet, mask, and range from configuration, validates range, computes address count through `SubnetUtils`, and returns either one zone per IP when range is zero or `ipCount / range`. `getReverseZoneNetworkAddress` validates range/index and offsets the base IP by `range * index`.

## State and persistence behavior
The class is stateless. Results are used by `RegistryDNS.addSplitReverseZones()` to create in-memory reverse DNS zones.

## Dependencies and integration points
It depends on Hadoop `Configuration`, Apache Commons Net `SubnetUtils`, Apache Commons Lang `StringUtils`, and DNS registry constants. `RegistryDNS` is the main consumer.

## Risks and test signals
IPv6 is explicitly unsupported. Range handling uses integer division, so non-even subnet/range combinations may leave uncovered addresses. Range zero has special meaning in subnet count but would be invalid for address stepping if used elsewhere. Tests should cover invalid IPs, IPv6 rejection, negative range/index, invalid subnet/mask, range zero, and split calculations across octet boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ReverseZoneUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/SecureableZone.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/SecureableZone.java

## Purpose
`SecureableZone` extends xbill `Zone` with record tracking needed for limited DNSSEC negative-response support through NXT records.

## Important APIs and types
Constructors mirror `Zone` constructors for zone transfers, remote transfers, master files, and record arrays. It overrides `addRecord` and `removeRecord` to maintain a local `List<Record> records`. `getNXTRecord(Record queryRecord, Zone zone)` computes an NXT record for a query insertion point.

## Control flow
On add/remove, the superclass zone is updated and the local records list is updated. `getNXTRecord` sorts the tracked records, binary-searches the query, chooses the insertion/base record, gathers existing RRset types at that base name, and returns an `NXTRecord` with the zone SOA minimum TTL.

## State and persistence behavior
State is in-memory only. The `records` list mirrors dynamic zone changes after construction, but constructor-loaded records may not be copied into the list until added through overridden methods.

## Dependencies and integration points
It depends on xbill DNS `Zone`, `Record`, `RRset`, `SetResponse`, `NXTRecord`, and transfer classes. `RegistryDNS.configureZone()` creates `SecureableZone` instances, and DNSSEC NXDOMAIN handling calls `getNXTRecord`.

## Risks and test signals
If `records` is null or incomplete for zones loaded from files/arrays, `getNXTRecord` may fail or produce incomplete NXT data. The list is not synchronized itself; callers rely on `RegistryDNS` locks. Tests should cover constructor-seeded zones, dynamic add/remove, NXT generation before/after first mutation, sorted insertion points, and concurrent access through `RegistryDNS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/SecureableZone.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ServiceRecordProcessor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ServiceRecordProcessor.java

## Purpose
`ServiceRecordProcessor` defines the contract for turning a registry `ServiceRecord` into DNS records managed by a `RegistryDNS.RegistryCommand`.

## Important APIs and types
Methods are `initTypeToInfoMapping(ServiceRecord)`, `getRecordTypes()`, and `manageDNSRecords(RegistryDNS.RegistryCommand)`.

## Control flow
Implementations initialize record descriptors from a service record, advertise valid DNS record types, and later execute add/remove commands for generated records. `BaseServiceRecordProcessor` provides the shared implementation for `manageDNSRecords`.

## State and persistence behavior
The interface has no state. Implementations normally hold transient descriptor state and mutate in-memory DNS zones through commands.

## Dependencies and integration points
It depends on `ServiceRecord`, `IOException`, and `RegistryDNS.RegistryCommand`. `RegistryDNS.op()` depends on this abstraction to choose application versus container processing.

## Risks and test signals
Implementations must make descriptor generation symmetric for add and remove. Tests should exercise the interface through `RegistryDNS.register` and `delete`, ensuring generated record identity is stable enough for removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ServiceRecordProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ZoneSelector.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ZoneSelector.java

## Purpose
`ZoneSelector` abstracts how DNS processors find the best matching DNS zone for a generated record name.

## Important APIs and types
The single method `findBestZone(Name name)` returns an xbill `Zone`.

## Control flow
`BaseServiceRecordProcessor.manageDNSRecords()` calls this method for every generated `Name` before executing a record add/remove command. `RegistryDNS` implements it by exact zone lookup followed by suffix lookup across labels.

## State and persistence behavior
The interface has no state. Implementations usually read in-memory zone maps.

## Dependencies and integration points
It depends on xbill `Name` and `Zone` and decouples processors from the concrete `RegistryDNS` zone map.

## Risks and test signals
A null result means record commands must handle no matching zone. Tests should verify exact, suffix, reverse-zone, and no-match behavior through the `RegistryDNS` implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ZoneSelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/package-info.java

## Purpose
This package descriptor documents DNS server classes for YARN application and service discovery through the registry.

## Important APIs and types
The package contains `RegistryDNS`, `RegistryDNSServer`, service-record processors, record creators, reverse-zone helpers, and privileged daemon startup support.

## Control flow
There is no executable code. The described package flow is: observe registry service records, translate them into DNS records, and serve DNS queries.

## State and persistence behavior
The package primarily maintains in-memory DNS zones derived from persistent registry entries in ZooKeeper.

## Dependencies and integration points
It integrates xbill DNS, registry client operations, YARN service-record attributes, and Hadoop service lifecycle.

## Risks and test signals
Package-level tests should combine an embedded registry with DNS query assertions to validate end-to-end discovery behavior, including add/update/delete events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/integration/SelectByYarnPersistence.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/integration/SelectByYarnPersistence.java

## Purpose
`SelectByYarnPersistence` is a `RegistryAdminService.NodeSelector` implementation that selects service records matching a specific YARN ID and persistence policy.

## Important APIs and types
Constructor arguments are `id` and `targetPolicy`, both required non-empty. `shouldSelect(String, RegistryPathStatus, ServiceRecord)` compares `serviceRecord.get(YARN_ID, "")` and `serviceRecord.get(YARN_PERSISTENCE, "")` to the configured values.

## Control flow
Registry admin cleanup code can instantiate this selector and pass candidate paths/status/records through `shouldSelect`. Only records with both matching ID and matching persistence policy are selected.

## State and persistence behavior
The selector stores immutable match criteria. It does not mutate registry state; `RegistryAdminService` would perform deletes for selected nodes.

## Dependencies and integration points
It depends on Apache Commons `StringUtils`, Hadoop `Preconditions`, `RegistryPathStatus`, `ServiceRecord`, `YarnRegistryAttributes`, and `RegistryAdminService.NodeSelector`.

## Risks and test signals
The path and status parameters are ignored, so selection is purely attribute-based. Tests should verify constructor validation, missing attributes returning false, exact string matching, and integration with admin cleanup deletion flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/integration/SelectByYarnPersistence.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/integration/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/integration/package-info.java

## Purpose
This package descriptor identifies classes that integrate the registry server with the YARN resource manager.

## Important APIs and types
In this subset, the main class is `SelectByYarnPersistence`, a selector useful for YARN lifecycle cleanup.

## Control flow
No executable code is present.

## State and persistence behavior
The package works with persistent service-record attributes to decide lifecycle actions, but this descriptor stores no state.

## Dependencies and integration points
Integration is between YARN lifecycle identifiers/policies and registry server administration.

## Risks and test signals
End-to-end cleanup tests should verify that YARN application, attempt, and container completion events translate into correct selector criteria and registry deletions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/integration/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/package-info.java

## Purpose
This package descriptor marks server-side registry components.

## Important APIs and types
It describes server-only or test-JVM components such as server-side ZooKeeper support, DNS support, and potential REST services.

## Control flow
There is no executable code.

## State and persistence behavior
Server components in this package family generally manage ZooKeeper-backed registry persistence or in-memory services derived from it.

## Dependencies and integration points
The package boundary separates deployed server/test support from registry client APIs and data types.

## Risks and test signals
Packaging tests should ensure client artifacts do not accidentally depend on server-only classes unless intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/AddingCompositeService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/AddingCompositeService.java

## Purpose
`AddingCompositeService` is a thin public subclass of Hadoop `CompositeService` that exposes add/remove service methods.

## Important APIs and types
The constructor accepts a service name. `addService(Service)` and `removeService(Service)` simply delegate to the superclass.

## Control flow
There is no additional behavior beyond standard `CompositeService` lifecycle management. The class exists to make child-service composition available to external classes.

## State and persistence behavior
State is inherited child-service lists and lifecycle state. It does not persist registry data.

## Dependencies and integration points
It depends on Hadoop service APIs and is useful for server/test components that need dynamic service composition.

## Risks and test signals
The class documentation warns that adding uninitialized services to an already initialized parent can break lifecycle transitions. Tests should cover add/remove visibility and lifecycle propagation in the intended usage contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/AddingCompositeService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/DeleteCompletionCallback.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/DeleteCompletionCallback.java

## Purpose
`DeleteCompletionCallback` is a Curator background callback that counts completed delete events and logs them at debug level.

## Important APIs and types
It implements `BackgroundCallback`. State is `AtomicInteger events`. `processResult(CuratorFramework, CuratorEvent)` increments the counter. `getEventCount()` returns the count.

## Control flow
When passed to a Curator delete operation, Curator invokes `processResult` asynchronously after completion, and the callback increments its event count regardless of event status.

## State and persistence behavior
Only an in-memory counter is maintained. It does not persist data or inspect delete success semantics beyond receiving an event.

## Dependencies and integration points
It depends on Curator framework/event APIs and is intended for registry admin async deletion flows.

## Risks and test signals
The counter increments for every callback event, including failures if Curator delivers them. Tests should verify callback invocation count and, where needed, pair it with event result-code assertions outside this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/DeleteCompletionCallback.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/MicroZookeeperService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/MicroZookeeperService.java

## Purpose
`MicroZookeeperService` runs a small embedded localhost ZooKeeper server under Hadoop service lifecycle and supplies registry binding information to clients.

## Important APIs and types
The class extends `AbstractService` and implements `RegistryBindingSource`, `RegistryConstants`, `ZookeeperConfigOptions`, and `MicroZookeeperServiceKeys`. Key methods are `serviceInit`, `setupSecurity`, `serviceStart`, `serviceStop`, `supplyBindingInformation`, `getConnectionString`, `getConnectionAddress`, and `getRandomAvailablePort`.

## Control flow
Initialization reads port, tick time, host, and data directory settings, creates instance/data/conf directories, and deletes explicit configured directories first. Start calls `setupSecurity()`, creates `FileTxnSnapLog` and `ZooKeeperServer`, configures and starts `ServerCnxnFactory`, builds `BindingInformation` with a fixed ensemble provider, records diagnostics, and writes the chosen quorum back into configuration. Stop shuts down the factory and deletes the data directory.

## State and persistence behavior
ZooKeeper transaction/snapshot data lives under the service data directory while running and is deleted on stop. Binding information is valid only after start. JVM system properties may be changed for secure embedded server setup.

## Dependencies and integration points
It integrates embedded ZooKeeper server classes, Curator `FixedEnsembleProvider`, Hadoop `FileUtil`, `RegistrySecurity` static helpers, registry constants, and `RegistryBindingSource`. It is suited for tests and local composite services that need a ZooKeeper-backed registry.

## Risks and test signals
Random-port selection has a bind race between closing the probe socket and ZooKeeper binding. Explicit instance directories are deleted during init. Secure setup mutates JVM-wide SASL properties and validates an existing JAAS context. Tests should cover start-before-binding failure, random and fixed ports, config quorum injection, secure/insecure startup, cleanup on stop, and diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/MicroZookeeperService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/MicroZookeeperServiceKeys.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/MicroZookeeperServiceKeys.java

## Purpose
`MicroZookeeperServiceKeys` defines configuration keys specific to the embedded `MicroZookeeperService`.

## Important APIs and types
The prefix is `RegistryConstants.REGISTRY_PREFIX + "zk.service."`. Keys include service JAAS context, tick time, host, port, data directory, and failed-SASL-client behavior. The default host is `localhost`.

## Control flow
There are no methods. `MicroZookeeperService` reads these constants during init and secure setup.

## State and persistence behavior
Values affect embedded ZooKeeper runtime state and data directory placement. They are not used by ordinary registry clients.

## Dependencies and integration points
The interface depends on `RegistryConstants` and is implemented by `MicroZookeeperService`.

## Risks and test signals
Misconfigured directories can be deleted by the service, and SASL keys affect JVM/server security behavior. Tests should cover defaults, custom host/port/dir, and secure server options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/MicroZookeeperServiceKeys.java -->
