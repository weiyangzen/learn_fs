# subset-b-007417 Research

Grouped research report for the exact source files assigned to work item `subset-b-007417`. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/RegistryAdminService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/RegistryAdminService.java

Purpose: `RegistryAdminService` extends the ZooKeeper-backed `RegistryOperationsService` with administrative registry setup, user home directory ACL management, asynchronous execution, and recursive purge support. It is the service-level owner of root registry paths such as `PATH_USERS` and `PATH_SYSTEM_SERVICES`.

Important APIs and types: constructors accept a service name and optional `RegistryBindingSource`; `submit()`, `createDirAsync()`, `initUserRegistryAsync()`, and `AsyncPurge` expose async operations through a cached `ExecutorService`; `createRootRegistryPaths()` initializes ZooKeeper nodes; `aclsForUser()` composes client ACLs plus secure-user ACLs; `PurgePolicy` and `NodeSelector` parameterize recursive deletion.

Control flow: service initialization adds a SASL all-permissions ACL for the current user when the registry is secure. Service start creates root paths and expands permission failures with registry diagnostics. Purge performs depth-first traversal: list children, try resolving the current record, ask the selector, handle child-bearing matches according to policy, delete if selected, then recurse into remaining children. It is defensive against concurrently removed paths by returning zero on `PathNotFoundException`.

State and persistence: persistent state lives in ZooKeeper nodes and ACLs; in-memory state is the executor. `stopExecutor()` uses `shutdownNow()` and does not wait for queued purge/create tasks. `initUserRegistry()` waits for the async task but assumes `initUserRegistryAsync()` returns a non-null future, so an already-existing home path can produce a null dereference risk.

Dependencies and integration: integrates with Curator callbacks, ZooKeeper ACL classes, Hadoop service lifecycle, registry security helpers, path utilities, and service record marshalling exceptions. Tests in this subset exercise operations indirectly through `AbstractRegistryTest`, `TestRegistryOperations`, and secure registry fixtures.

Risks and test signals: purge behavior is sensitive to selector correctness, concurrent deletion, and the chosen child policy. Secure startup depends on realm discovery and current-user SASL identity. Test coverage validates root path setup, registry CRUD, ACL/security helpers, and YARN persistence selector logic, but explicit tests for `initUserRegistry()` idempotency and async executor shutdown behavior are not visible here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/RegistryAdminService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/package-info.java

Purpose: package documentation describes basic services for the YARN registry server services package. It establishes the conceptual roles of registry admin, embedded ZooKeeper, and composite service helpers.

Important APIs and types: references `RegistryAdminService`, `MicroZookeeperService`, and `AddingCompositeService`. It does not declare code, state, or methods, but it is a public documentation integration point for generated Javadocs.

Control flow and state: no executable flow or persistence. The behavior described maps to registry administrative actions, test ZooKeeper lifecycle, and public add/remove service aggregation in the referenced classes.

Dependencies and integration: documents service-layer coupling with YARN/Hadoop service lifecycles and ZooKeeper-backed registry operations.

Risks and test signals: risks are documentation drift if package-level descriptions stop matching the classes. The tests in this subset instantiate both `RegistryAdminService` and `MicroZookeeperService`, indirectly confirming the package summary still points at active classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/services/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/AbstractRegistryTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/AbstractRegistryTest.java

Purpose: common base fixture for ZooKeeper-backed registry operation tests. It creates a fresh `RegistryAdminService`, resets the registry tree, recreates root paths, and exposes helper assertions and record bind helpers.

Important APIs and functions: `setupRegistry()` initializes and starts the admin service with `createRegistryConfiguration()` from `AbstractZKRegistryTest`; `putExampleServiceEntry()` builds and binds a sample `ServiceRecord`; `assertPathExists()`, `assertPathNotFound()`, and `assertResolves()` wrap registry calls in test-friendly assertions.

Control flow: each test starts with an initialized in-memory ZooKeeper from the superclass. The fixture deletes `/` recursively, then calls `createRootRegistryPaths()` to isolate tests. Binding helpers ensure the parent path exists before calling `operations.bind()`.

State and persistence: persists test data in the shared `MicroZookeeperService` instance, then cleans through service teardown registration. The `registry` and `operations` fields share the same object.

Dependencies and integration: integrates registry admin services, `RegistryOperations`, path utilities, persistence policies, and JUnit lifecycle annotations.

Risks and test signals: deleting `/` and recreating root paths is a broad reset, so tests depend on `RegistryAdminService` being robust after full tree deletion. This fixture is a strong signal for normal registry CRUD behavior but not for multi-client or secure ACL behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/AbstractRegistryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/AbstractZKRegistryTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/AbstractZKRegistryTest.java

Purpose: base fixture for tests requiring a transient ZooKeeper server. It owns class-level startup and teardown of `MicroZookeeperService` and produces registry client configurations bound to that instance.

Important APIs and functions: static `createZKServer()` creates `target/zookeeper`, initializes `MicroZookeeperService`, and registers it with an `AddingCompositeService`; `teardownServices()` closes all registered services; `getConnectString()` and `createRegistryConfiguration()` provide client connection settings.

Control flow: static composite service starts before `@BeforeAll` runs, then receives ZooKeeper and any other test services. Each test renames the current thread to `JUnit`, which helps diagnostics. Registry retry and timeout settings are kept low for tests.

State and persistence: ZooKeeper data is stored under `target/zookeeper` and deleted before the server starts. Service state is class-static, so subclasses share one server per test class.

Dependencies and integration: uses Hadoop `Configuration`, registry constants, `RegistryConfiguration`, and the service lifecycle. `AbstractRegistryTest` and `TestCuratorService` depend on it.

Risks and test signals: class-level sharing can hide cross-test leakage if a subclass fails to reset data; however, root deletion in `AbstractRegistryTest` reduces that risk for operation tests. Timeout of 10 seconds catches ZooKeeper startup or client hang regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/AbstractZKRegistryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/RegistryTestHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/RegistryTestHelper.java

Purpose: shared assertions, sample records, endpoint builders, Kerberos login helpers, and logging utilities for registry tests.

Important APIs and functions: constants define canonical test paths and endpoint APIs. `validateEntry()`, `assertMatches()`, and `findEndpoint()` verify service-record structure. `buildExampleServiceEntry()` and `addSampleEndpoints()` create realistic external and internal endpoints. Kerberos helpers include `enableKerberosDebugging()`, `logout()`, and `loginUGI()`.

Control flow: record validation locates endpoints by API, checks address/protocol types, tuple counts, and selected address values. Record comparison checks description, attributes, and endpoint counts, but does not deeply compare every endpoint field. Sample endpoint creation mixes URI, REST, Thrift, hostname/port, and IPC endpoint builders.

State and persistence: no persistent state beyond a static `ServiceRecordMarshal` and constants. Login helpers can change JVM security debug properties and create UGI login state through Hadoop security.

Dependencies and integration: integrates `RegistryTypeUtils`, `RegistryUtils`, YARN registry attributes, JUnit assertions, ZooKeeper path validation, JAAS login context, and Hadoop UGI.

Risks and test signals: helpers are heavily reused, so assertion gaps can propagate. `createRecord(String id, String persistence, String description, String data)` ignores `data`, which is safe for current tests but may surprise future test authors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/RegistryTestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/cli/TestRegistryCli.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/cli/TestRegistryCli.java

Purpose: validates the command-line registry client against a live in-memory registry from `AbstractRegistryTest`.

Important APIs and functions: `setUp()` creates captured stdout/stderr streams and instantiates `RegistryCli`; `assertResult()` checks CLI exit codes; tests cover bad command names, invalid argument counts, invalid argument values, bad paths, missing paths, and successful `bind`, `resolve`, `rm`, and `mknode` flows.

Control flow: valid command tests repeatedly bind records of `-inet`, `-webui`, and `-rest` endpoint forms, resolve them, remove them, and confirm subsequent resolution fails. It also tests binding records under subdirectories and binding directly to an existing directory node.

State and persistence: all CLI actions mutate the registry service created by the superclass. The test captures output but only asserts status codes, not emitted text.

Dependencies and integration: integrates `RegistryCli`, registry operations, registry configuration, endpoint parser options, and JUnit lifecycle. It indirectly exercises service record creation by CLI command parsing.

Risks and test signals: strong coverage for command validation and basic registry mutation. It does not verify output formatting, stderr diagnostics, or stream restoration after `System.setOut(sysOut)`, so global stdout side effects are a possible test hygiene risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/cli/TestRegistryCli.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/binding/TestMarshalling.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/binding/TestMarshalling.java

Purpose: tests JSON marshalling and validation of registry `ServiceRecord` instances.

Important APIs and functions: class-level `ServiceRecordMarshal`; `testRoundTrip()` validates serialization/deserialization of custom attributes; negative tests cover empty bytes, truncated JSON, invalid JSON, wrong type, long nonmatching type, missing service record type, and wrong validation type. Additional tests verify unknown field round-trip and copy constructor propagation.

Control flow: positive paths create a record, validate it with `RegistryTypeUtils`, serialize to bytes, deserialize, and compare attributes and endpoint counts. Negative paths assert specific registry exceptions (`NoRecordException` or `InvalidRecordException`).

State and persistence: all state is in-memory byte arrays and `ServiceRecord` objects. No external registry dependency.

Dependencies and integration: depends on `RegistryUtils.ServiceRecordMarshal`, `ServiceRecord`, persistence policies, helper assertions, and registry record validation code.

Risks and test signals: good signal for malformed input handling and custom attribute preservation. It does not test very large records, Unicode payloads, or compatibility with external JSON libraries beyond the local marshal implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/binding/TestMarshalling.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/binding/TestRegistryOperationUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/binding/TestRegistryOperationUtils.java

Purpose: unit tests small user-name utility behavior in `RegistryUtils`.

Important APIs and functions: `getCurrentUsernameUnencoded()` is tested for explicit override and current UGI fallback; `convertUsername()` is tested for stripping Kerberos realm and host components while preserving ordinary names with spaces.

Control flow: assertions compare utility output to either a literal override or `UserGroupInformation.getCurrentUser().getShortUserName()`.

State and persistence: no persisted state. It reads current process UGI, making one assertion environment-dependent by design.

Dependencies and integration: integrates Hadoop security UGI and registry binding utilities.

Risks and test signals: covers primary normalization cases used by home path generation. It does not test lowercasing, path encoding, or invalid user strings; those are covered in neighboring path utility and operation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/binding/TestRegistryOperationUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/binding/TestRegistryPathUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/binding/TestRegistryPathUtils.java

Purpose: tests registry path construction, parsing, encoding, username extraction, and DNS-style validation helpers.

Important APIs and functions: static imports from `RegistryPathUtils` cover `encodeForRegistry`, `createFullPath`, `split`, `parentOf`, `lastPathEntry`, `validateZKPath`, and `validateElementsAsDNS`. Tests include ASCII, punycode-style non-ASCII encoding, idempotence, path joining edge cases, username extraction, splitting with repeated slashes, and invalid path elements.

Control flow: helpers assert expected generated paths and assert either successful validation or `InvalidPathnameException`. `parentOf("/")` is expected to throw `PathNotFoundException`.

State and persistence: pure in-memory string tests.

Dependencies and integration: validates utility assumptions used by registry CRUD, CLI path checks, and user-home path generation.

Risks and test signals: strong signal for normalized slash handling and path component rules. Tests intentionally leave numeric root component validity ambiguous in a comment, indicating path policy edge cases may still need product-level clarification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/binding/TestRegistryPathUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/CuratorEventCatcher.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/CuratorEventCatcher.java

Purpose: test callback utility for capturing asynchronous Curator events.

Important APIs and functions: implements `BackgroundCallback.processResult()`, increments an `AtomicInteger`, and enqueues the `CuratorEvent` into a single-capacity `LinkedBlockingQueue`; `getCount()` and `take()` expose event count and blocking retrieval.

Control flow: Curator invokes `processResult()` on background completion. The event is logged, counted, and put into the queue. Tests can block on `take()` until the event arrives.

State and persistence: state is in-memory only: one blocking queue and an atomic counter. Queue capacity of one can block callback threads if more than one event arrives before tests drain it.

Dependencies and integration: used by `TestCuratorService.testBackgroundDelete()` to verify background delete callbacks.

Risks and test signals: useful for single-event async tests. It is intentionally minimal and not safe as a general multi-event collector unless tests consume promptly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/CuratorEventCatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/TestCuratorService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/TestCuratorService.java

Purpose: integration-style tests for low-level ZooKeeper/Curator wrapper operations in `CuratorService`.

Important APIs and functions: fixture creates a `CuratorService` connected to the micro ZooKeeper. Tests cover `zkList`, existence checks, `zkPathMustExist`, path creation with persistent and ephemeral modes, `maybeCreate`, recursive and nonrecursive delete, background delete callbacks, create, duplicate create, update, and use of a `MicroZookeeperService` as binding source.

Control flow: each test starts a fresh curator and ensures root exists with world read/write ACL. Delete tests distinguish leaf deletion, nonrecursive failure on children, and recursive success. Update tests allow setting data on directory nodes, including nodes with children.

State and persistence: all mutations occur in the shared test ZooKeeper namespace. Root ACLs are permissive test ACLs. Service is stopped after each test.

Dependencies and integration: integrates Curator, ZooKeeper `CreateMode`, Hadoop path exceptions, registry security ACL constants, and `CuratorEventCatcher`.

Risks and test signals: strong coverage of wrapper exception mapping and idempotent delete semantics. It does not deeply assert node data contents after update, only operation success/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/TestCuratorService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/TestFSRegistryOperationsService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/TestFSRegistryOperationsService.java

Purpose: tests the filesystem-backed registry implementation using the local filesystem.

Important APIs and functions: class-level `FSRegistryOperationsService` and `FileSystem`; tests cover `mknode`, `bind`, `resolve`, `exists`, `delete`, and `list`. A private `createRecord()` builds simple `ServiceRecord` instances with YARN IDs.

Control flow: test setup creates a local `test` directory and teardown deletes it. Bind tests verify parent creation behavior, overwrite behavior, and `_record` file creation. Delete tests distinguish directory-only children from `_record` files and assert nonrecursive deletion failures.

State and persistence: persists test directories and `_record` files under local path `test`. The registry service itself is static, but the filesystem tree is reset around each test.

Dependencies and integration: integrates Hadoop `FileSystem`, registry service-record serialization, Hadoop path exceptions, and JUnit assertions.

Risks and test signals: provides useful parity checks for the non-ZooKeeper backend. It catches behavior around `_record` pseudo-files, but tests catch broad `IOException` in several places, so precise exception type regressions could slip through.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/TestFSRegistryOperationsService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/TestMicroZookeeperService.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/TestMicroZookeeperService.java

Purpose: smoke test for the embedded `MicroZookeeperService` default temporary directory support.

Important APIs and functions: `testTempDirSupport()` creates, initializes, starts, and stops a `MicroZookeeperService` using a `RegistryConfiguration`; `destroyZKServer()` stops the service after each test.

Control flow: service lifecycle is exercised without explicit ZooKeeper path operations.

State and persistence: any storage is managed internally by `MicroZookeeperService` default configuration. The field is stopped through `ServiceOperations.stop()`.

Dependencies and integration: integrates registry configuration, Hadoop service operations, and JUnit timeout.

Risks and test signals: this is a basic lifecycle signal only. It does not validate connection strings, directory cleanup, port binding, or client connectivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/TestMicroZookeeperService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/integration/TestYarnPolicySelector.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/integration/TestYarnPolicySelector.java

Purpose: tests `SelectByYarnPersistence`, a `RegistryAdminService.NodeSelector` used by purge logic to select service records by YARN ID and persistence policy.

Important APIs and functions: fixture creates a `ServiceRecord` with ID `1` and `APPLICATION` persistence plus a `RegistryPathStatus`. `assertSelected()` invokes `selector.shouldSelect()`. Tests cover nonmatching persistence, matching app persistence, and nonmatching app ID.

Control flow: direct selector invocation avoids ZooKeeper traversal and isolates matching rules.

State and persistence: pure in-memory record and status.

Dependencies and integration: connects YARN persistence constants to registry admin purge selection. This is the unit-level counterpart to purge traversal in `RegistryAdminService`.

Risks and test signals: good signal for exact ID/persistence matching. It does not test wildcard behavior, null record fields, or integration with actual purge recursion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/integration/TestYarnPolicySelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/operations/TestRegistryOperations.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/operations/TestRegistryOperations.java

Purpose: main operation test suite for ZooKeeper-backed `RegistryOperations`.

Important APIs and functions: tests exercise service record put/get/delete, stat/list, recursive delete, missing-path exceptions, mkdir semantics, minimal records, overwrite flags, persistence policies, accessors, full child listing with statuses, and complex username-derived paths.

Control flow: tests use the `AbstractRegistryTest` fixture. Record tests create parent paths, bind records, resolve them, validate endpoint structure, and compare attributes. Listing tests combine raw child names, `RegistryUtils.statChildren()`, and `RegistryUtils.extractServiceRecords()`. Negative tests assert `PathNotFoundException`, `NoRecordException`, `FileAlreadyExistsException`, or `PathIsNotEmptyDirectoryException`.

State and persistence: all test state is ZooKeeper registry nodes and serialized service records under the reset test root.

Dependencies and integration: integrates bind flags, path utilities, registry utils, service-record validation, YARN persistence attributes, and path encoding.

Risks and test signals: broad signal for registry API behavior. It covers complex names including spaces, underscores, backslashes, Kerberos names, and non-ASCII-derived home paths. Deep ACL behavior and purge-specific behavior are outside this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/operations/TestRegistryOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/AbstractSecureRegistryTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/AbstractSecureRegistryTest.java

Purpose: shared fixture for Kerberos-secured registry and ZooKeeper tests. It provisions a MiniKdc, principals, keytabs, JAAS file, Hadoop security configuration, and secure `MicroZookeeperService` instances.

Important APIs and functions: class setup initializes `RegistrySecurity`, KDC, JAAS system properties, and Kerberos rules. `setupKDCAndPrincipals()` creates keytabs for ZooKeeper, Alice, and Bob and writes JAAS entries. `createSecureZKInstance()` configures a secure micro ZooKeeper. `login()` creates a JAAS `LoginContext`; `startSecureZK()` logs in the ZooKeeper server principal and starts the secure service.

Control flow: class lifecycle starts security once; instance lifecycle stops per-test services and secure ZooKeeper. Principal choice differs on Windows for localhost versus 127.0.0.1. Kerberos short-name mapping uses a fixed rule that strips the `EXAMPLE.COM` realm.

State and persistence: writes KDC work files, keytabs, and `jaas.txt` under `target/kdc` or `test.dir`. It mutates JVM JAAS and Hadoop security state.

Dependencies and integration: integrates MiniKdc, Hadoop UGI, KerberosName, registry security, ZooKeeper SASL options, service lifecycle, and test name extension.

Risks and test signals: expensive and environment-sensitive but necessary for secure registry coverage. Global JVM security properties and Kerberos rules can leak if teardown is incomplete; the fixture explicitly stops services and clears login state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/AbstractSecureRegistryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/KerberosConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/KerberosConfiguration.java

Purpose: test-only JAAS `Configuration` implementation for Kerberos client and server logins.

Important APIs and functions: factory methods `createClientConfig()` and `createServerConfig()` set `isInitiator`; `getAppConfigurationEntry()` returns one required Krb5 login module entry with JVM-specific options; `toString()` reports the principal.

Control flow: IBM Java gets `useKeytab`, `credsType`, and optional `useDefaultCcache`; other JVMs get `keyTab`, `useKeyTab`, `storeKey`, `doNotPrompt`, `useTicketCache`, `renewTGT`, `refreshKrb5Config`, and `isInitiator`. If `KRB5CCNAME` is present, ticket cache options are added.

State and persistence: stores principal, absolute keytab path, and initiator flag. May set the `KRB5CCNAME` system property on IBM Java.

Dependencies and integration: used by secure registry tests to create `LoginContext` instances. It depends on Hadoop `KerberosUtil` and platform detection.

Risks and test signals: option differences across JVMs are a portability risk. Debug is always enabled, which is helpful for tests but noisy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/KerberosConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/TestRegistrySecurityHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/TestRegistrySecurityHelper.java

Purpose: unit tests registry security ACL parsing, default realm expansion, UGI ACL creation, and secure configuration validation.

Important APIs and functions: class setup initializes `RegistrySecurity` as secure with a configured realm. Tests cover `splitAclPairs()`, `buildACLs()`, default realm insertion for SASL ACLs, mixed SASL/digest ACLs, default system accounts, JVM realm lookup, `createACLForUser()`, and the requirement that secure registry implies Kerberos authentication.

Control flow: ACL strings are split and built into ZooKeeper `ACL` objects, then IDs and schemes are asserted. Null realm with short SASL principals is expected to fail during ACL building.

State and persistence: no persistent external state; it initializes a test `RegistrySecurity` instance and reads current UGI/JVM realm.

Dependencies and integration: ties registry constants, ZooKeeper ACL permissions, Hadoop UGI, and `RegistrySecurity` parsing rules together.

Risks and test signals: strong parser coverage for realmed and short ACL strings. It does not run against a live secure ZooKeeper, so enforcement is covered separately by secure registry integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/TestRegistrySecurityHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/TestSecureLogins.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/TestSecureLogins.java

Purpose: validates Kerberos login plumbing used by secure registry tests.

Important APIs and functions: tests verify realm availability, JAAS file binding, Alice and ZooKeeper `LoginContext` creation, direct Krb5 login module reflection, default realm lookup, Kerberos rule configuration, valid Kerberos short-name parsing under Hadoop and MIT mechanisms, and keytab-based UGI login plus SASL ACL creation.

Control flow: login tests create contexts from keytabs, log subject details, set ZooKeeper SASL client properties, and always log out. `testKerberosAuth()` reflects into the Krb5 login module and manually calls `initialize`, `login`, and `commit` with platform-specific options.

State and persistence: relies on MiniKdc/keytabs/JAAS from the superclass. It mutates Kerberos rule mechanism and resets it to the default mechanism.

Dependencies and integration: integrates MiniKdc, JAAS, Hadoop UGI, HadoopKerberosName, KerberosUtil, ZooKeeper environment keys, and registry security ACL helpers.

Risks and test signals: strong end-to-end signal for local Kerberos setup. Reflection into JDK login modules and default realm lookup are environment-sensitive; failures may indicate platform/security setup rather than registry code defects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/TestSecureLogins.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/TestSecureRegistry.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/TestSecureRegistry.java

Purpose: integration tests secure `MicroZookeeperService` startup and Curator client behavior against SASL-enabled ZooKeeper.

Important APIs and functions: tests cover creating secure ZooKeeper, connecting with an insecure client after root creation, ZooKeeper principal write access, and SASL system property overwrite semantics. Helper `startCuratorServiceInstance()` configures a Curator client against `secureZK`; `userZookeeperToCreateRoot()` logs in as ZooKeeper and creates `/`.

Control flow: tests enable Kerberos debugging before each run and clear ZooKeeper SASL properties afterward. Secure paths log in through `LoginContext`, set SASL client properties, start Curator, create paths, and clean up login/client state in finally blocks.

State and persistence: mutates secure ZooKeeper state, JVM SASL system properties, and login contexts. Root ACLs are world read/write for test accessibility.

Dependencies and integration: integrates secure fixture, `CuratorService`, `RegistrySecurity`, ZooKeeper SASL option constants, and path dumping diagnostics.

Risks and test signals: covers secure startup and client property behavior. The insecure-client test is deliberately permissive after root creation, so it should not be interpreted as full ACL enforcement coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/secure/TestSecureRegistry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/server/dns/TestRegistryDNS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/server/dns/TestRegistryDNS.java

Purpose: comprehensive tests for `RegistryDNS`, converting YARN registry `ServiceRecord` data into DNS records and replies.

Important APIs and functions: fixture initializes `RegistryDNS`, domain name, zones, TTL, and a service-record marshal. Tests cover application registration, container registration, missing persistence, TTLs, reverse PTR lookup, large-network reverse zones, missing reverse records, records without IPs, DNSKEY signing primitives, IPv4-to-IPv6 mapping, AAAA lookup, negative lookup authority SOA, reading master zone files, reverse zone name calculation, split reverse zones, external CNAME, root NS lookup, multiple A records, and upstream fault behavior.

Control flow: tests marshal JSON service records, call `registryDNS.register(path, record)`, build dnsjava `Message` queries, invoke `generateReply()`, and inspect RCODE, questions, answer sections, record types, TTLs, and signatures. `assertDNSQuery()` doubles expected answer count when DNSSEC is enabled by subclasses.

State and persistence: dynamic DNS state is held inside `RegistryDNS` zones and stopped after each test. Some tests read static zone resources and DNSSEC private key resources from the test classpath.

Dependencies and integration: integrates registry constants, YARN service record attributes, dnsjava record types, DNSSEC, RSA keys, reverse-zone utilities, and `BaseServiceRecordProcessor`.

Risks and test signals: very strong behavior signal for DNS mapping and negative responses. Tests rely on fixed static JSON and test resource files; changes in dnsjava ordering or DNSSEC output can affect assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/server/dns/TestRegistryDNS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/server/dns/TestReverseZoneUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/server/dns/TestReverseZoneUtils.java

Purpose: unit tests reverse DNS zone address calculations.

Important APIs and functions: tests `ReverseZoneUtils.getReverseZoneNetworkAddress()` and `splitIp()`.

Control flow: assertions cover normal base address calculation, splitting IPv4 octets into long values, negative index rejection, invalid IP rejection, negative range rejection, and several range/index combinations.

State and persistence: pure string/numeric utility tests.

Dependencies and integration: supports `RegistryDNS` split reverse-zone setup and reverse lookup tests.

Risks and test signals: good coverage for arithmetic boundaries and validation. It does not test IPv6 or subnet-mask-derived ranges directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/server/dns/TestReverseZoneUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/server/dns/TestSecureRegistryDNS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/server/dns/TestSecureRegistryDNS.java

Purpose: DNSSEC-enabled variant of `TestRegistryDNS`.

Important APIs and functions: overrides `createConfiguration()` to set `KEY_DNSSEC_ENABLED`, public DNSSEC key material, and private key file resource; overrides `isSecure()` to return true.

Control flow: inherits all parent DNS tests, causing `assertDNSQuery()` to expect RRSIG records and doubled answer counts for secure responses.

State and persistence: uses the same dynamic registry DNS state as the parent plus test classpath private key resource.

Dependencies and integration: integrates DNSSEC configuration constants with the entire registry DNS test matrix.

Risks and test signals: high-value regression signal because one subclass exercises many DNS paths with signing enabled. Its key material is static test data; missing `/test.private` resource will fail inherited tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/server/dns/TestSecureRegistryDNS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/pom.xml

Purpose: Maven aggregator POM for the Hadoop common project.

Important configuration: parent is `hadoop-project` version `3.6.0-SNAPSHOT`; artifact is `hadoop-common-project`; packaging is `pom`; modules include `hadoop-auth`, `hadoop-auth-examples`, `hadoop-common`, `hadoop-annotations`, `hadoop-nfs`, `hadoop-minikdc`, `hadoop-kms`, and `hadoop-registry`.

Control flow and build behavior: as an aggregator, it participates in Maven module traversal and inherits most build behavior from the parent. The deploy plugin is configured with `skip=true`, so this aggregator itself is not deployed. The Apache RAT plugin is present with an empty configuration block.

State and persistence: no runtime state. Build output and module graph are determined by Maven execution.

Dependencies and integration: integrates the registry module researched above into the common project build and makes MiniKdc available as a sibling module for secure tests.

Risks and test signals: changes to module order or parent path affect multi-module builds. Empty RAT configuration delegates policy to inherited defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/dev-support/findbugsExcludeFile.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs suppression file for known or accepted HDFS client warnings.

Important entries: suppresses exposed representation warnings for protocol/value classes including `XAttr`, `LocatedBlock`, HDFS statuses, snapshot reports, storage reports, and block token/data encryption key types; suppresses generated protobuf warning patterns; suppresses unreleased-lock warnings for `DfsClientShmManager.EndpointShmManager.allocSlot`; suppresses selected mutable static, catch-exception, inconsistent-sync, transient-field, and byte-array exposure warnings.

Control flow and state: no executable runtime behavior. It controls static analysis output in the build/dev-support lane.

Dependencies and integration: referenced by HDFS client quality tooling. The module POM excludes this file from RAT checks, recognizing it as dev-support metadata.

Risks and test signals: suppressions can hide real regressions if code changes invalidate the original rationale. Comments provide intent for several suppressions, but broad `EI_EXPOSE_REP` class suppressions should be revisited when public mutability contracts change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/pom.xml

Purpose: Maven module definition for the Hadoop HDFS client jar.

Important configuration: parent is `hadoop-project-dist`; artifact is `hadoop-hdfs-client`; component property is `hdfs`; packaging is `jar`. Dependencies include provided `hadoop-common`, Apache HTTP client/core, Jakarta JAX-RS API, Jackson annotations/databind, JUnit 5, Mockito inline, Netty test dependencies, MockServer, and Hadoop common test jar.

Control flow and build behavior: Surefire is declared for tests. RAT excludes `dev-support/findbugsExcludeFile.xml`. Protobuf plugin compiles sources with an additional proto path to common protos. Maven replacer runs on generated, main, and test sources. Javadoc excludes generated protocol protobuf packages.

State and persistence: no runtime state; defines build graph, generated sources, and test dependencies.

Dependencies and integration: supports HDFS client classes such as `Hdfs`, WebHDFS wrappers, protocol types, and RPC/protobuf alignment context code.

Risks and test signals: dependency scope choices are important: `hadoop-common` is provided for main code but test jar is test-scoped. Generated proto and replacer execution are essential for protocol classes used by `ClientGSIContext`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/CacheFlag.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/CacheFlag.java

Purpose: public evolving enum for cache directive operation flags.

Important APIs and types: only enum value is `FORCE`, documented to ignore cache pool resource limits. Each flag holds a short mode, exposed package-locally through `getMode()`.

Control flow and state: no dynamic control flow beyond enum construction. Mode value `0x01` is used for protocol/operation encoding by neighboring cache directive code.

Dependencies and integration: annotated public/evolving and intended for `EnumSet<CacheFlag>` composition in cache APIs.

Risks and test signals: small surface, but mode stability matters for wire or server interpretation. `getMode()` is package-private, constraining external callers to enum constants rather than numeric values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/CacheFlag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/Hdfs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/Hdfs.java

Purpose: `AbstractFileSystem` implementation for the `hdfs` URI scheme, delegating filesystem operations to `DFSClient`.

Important APIs and functions: constructor validates scheme/host and creates `DFSClient`; overrides create, delete, block locations, checksum, status, link status, filesystem status/defaults, listing, corrupt block listing, mkdir, open, truncate, rename, owner/permission/replication/times, checksum verification, symlinks, canonical service name, delegation tokens, ACLs, xattrs, access checks, storage policies, token renew/cancel, and snapshots.

Control flow: most methods translate `Path` to URI path and call `DFSClient`. Listing has notable batching behavior: `DirListingIterator` fetches first batch and lazily fetches more when exhausted; `listStatus()` eagerly accumulates all batches into an array and throws if the directory disappears between batches. File status methods convert `HdfsFileStatus` into qualified `FileStatus` objects and throw `FileNotFoundException` on null.

State and persistence: state is a `DFSClient` and mutable `verifyChecksum` flag. Persistent data lives in HDFS NameNode/DataNode state, not in this wrapper. Delegation token operations affect HDFS security token lifecycle.

Dependencies and integration: integrates FileContext `AbstractFileSystem`, `DFSClient`, HDFS protocol statuses, ACL/xattr/storage policy APIs, token APIs, corrupt block iterator, and HDFS configuration initialization.

Risks and test signals: wrapper correctness depends on consistent path translation and exception mapping. `getDelegationTokens()` adds the returned token without null filtering, so callers must tolerate whatever `DFSClient.getDelegationToken()` returns. No tests in this subset directly exercise `Hdfs`; coverage likely lives elsewhere in HDFS client tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/Hdfs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/HdfsBlockLocation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/HdfsBlockLocation.java

Purpose: `BlockLocation` wrapper that carries the underlying HDFS `LocatedBlock` for clients that need HDFS-specific block detail.

Important APIs and functions: constructor copies a `BlockLocation` and stores a transient `LocatedBlock`; `getLocatedBlock()` exposes it; custom `readObject()` clears the transient block after deserialization; `isStriped()` delegates to `block.isStriped()`.

Control flow and state: serialization restores only the base `BlockLocation` state and sets `block` to null because `LocatedBlock` is not serializable.

Dependencies and integration: integrates common filesystem block location APIs with HDFS protocol block metadata.

Risks and test signals: after deserialization, `getLocatedBlock()` returns null and `isStriped()` will throw a null dereference. Callers need to avoid `isStriped()` on deserialized instances or the method needs defensive behavior elsewhere. FindBugs suppressions mention transient field restoration for related block location status classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/HdfsBlockLocation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/SWebHdfs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/SWebHdfs.java

Purpose: public evolving `AbstractFileSystem` adapter for secure WebHDFS using scheme `swebhdfs`.

Important APIs and functions: package-private constructor required by `AbstractFileSystem#createFileSystem()` delegates to `DelegateToFileSystem`; static `createSWebHdfsFileSystem()` instantiates `SWebHdfsFileSystem` and sets configuration.

Control flow and state: construction creates a fresh underlying filesystem object and delegates operations through `DelegateToFileSystem`. The wrapper itself stores no custom state beyond superclass state.

Dependencies and integration: integrates FileContext AFS resolution, `SWebHdfsFileSystem`, URI scheme registration, and Hadoop configuration.

Risks and test signals: very small adapter surface. Correctness depends on scheme registration and `SWebHdfsFileSystem` implementation. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/SWebHdfs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/WebHdfs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/WebHdfs.java

Purpose: public evolving `AbstractFileSystem` adapter for WebHDFS using scheme `webhdfs`.

Important APIs and functions: constructor delegates to `DelegateToFileSystem` with a newly configured `WebHdfsFileSystem`; `SCHEME` names the URI scheme.

Control flow and state: instantiation sets configuration on the underlying filesystem and lets the superclass handle operation delegation. No additional persistence or mutable fields.

Dependencies and integration: connects FileContext AFS creation with `WebHdfsFileSystem`.

Risks and test signals: minimal code; risk is mostly registration/configuration mismatch. Secure behavior belongs in `SWebHdfs`, not here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/WebHdfs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/XAttr.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/XAttr.java

Purpose: private model of a POSIX-style extended attribute with namespace, name, and optional byte-array value.

Important APIs and types: `NameSpace` enum defines `USER`, `TRUSTED`, `SECURITY`, `SYSTEM`, and `RAW`. `Builder` sets namespace, name, and value, then builds an immutable `XAttr` reference object. Getters expose the fields; `equals()`, `hashCode()`, `equalsIgnoreValue()`, and `toString()` support comparison and diagnostics.

Control flow and state: builder defaults namespace to `USER`. Constructed fields are final, but the byte-array `value` is stored and returned directly.

Dependencies and integration: used by HDFS xattr APIs and protocol conversion code. FindBugs suppression explicitly accepts representation exposure for `XAttr` and `XAttr.Builder`.

Risks and test signals: mutability of the exposed byte array means `XAttr` is not deeply immutable. Equality includes byte-array content; `equalsIgnoreValue()` allows namespace/name matching for operations that do not care about current value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/XAttr.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/AddBlockFlag.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/AddBlockFlag.java

Purpose: private evolving enum of hints for NameNode block allocation and replica placement.

Important APIs and types: values are `NO_LOCAL_WRITE`, `IGNORE_CLIENT_LOCALITY`, and `NO_LOCAL_RACK`, each with a short mode. `valueOf(short)` maps wire/encoded mode back to enum or returns null; `getMode()` exposes the short.

Control flow and state: simple enum lookup loops over all values. Modes are stable protocol-adjacent values used by `ClientProtocol#addBlock()`.

Dependencies and integration: references `CreateFlag` equivalents and HDFS `ClientProtocol.addBlock`.

Risks and test signals: returning null for unknown modes makes caller handling important. `NO_LOCAL_RACK` uses mode `0x03`, not a bitmask combination in this enum, so consumers should treat modes as enum identifiers unless protocol code documents otherwise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/AddBlockFlag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/BlockMissingException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/BlockMissingException.java

Purpose: private evolving `IOException` thrown when a read encounters a block with no available locations.

Important APIs and functions: constructor takes filename, description, and offset; `getFile()` and `getOffset()` expose the affected file and corruption offset.

Control flow and state: no custom flow beyond exception construction. Filename and offset are final and serializable with the exception.

Dependencies and integration: used by DFS read paths to report missing block location failures to callers.

Risks and test signals: accurate filename/offset population is critical for client retry and diagnostics. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/BlockMissingException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/BlockReader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/BlockReader.java

Purpose: private interface for reading a single HDFS block from a single DataNode.

Important APIs and functions: extends `ByteBufferReadable` and `Closeable`; defines byte-array `read`, `skip`, `available`, `close`, `readFully`, `readAll`, `isShortCircuit`, `getClientMmap`, `getDataChecksum`, and `getNetworkDistance`.

Control flow contract: implementations must return `-1` at EOF even for zero-byte reads. Comments acknowledge a checksum caveat: implementations may modify the user buffer before detecting checksum failure because data is read before checksum verification.

State and persistence: interface only. Implementations own sockets, local file descriptors, checksum state, mmap handles, and DataNode distance metadata.

Dependencies and integration: used by `DFSInputStream` read paths, short-circuit local reads, mmap support, read options, and checksum validation.

Risks and test signals: the buffer-before-checksum behavior is a correctness contract clients need to understand. Implementations must keep `readFully`/`readAll` semantics distinct to avoid EOF and partial-read bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/BlockReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/CannotObtainBlockLengthException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/CannotObtainBlockLengthException.java

Purpose: public unstable `IOException` indicating that a `LocatedBlock` length could not be obtained.

Important APIs and functions: constructors support no-arg, message-only, located-block, and located-block-with-source-file variants.

Control flow and state: no custom behavior beyond message construction. `serialVersionUID` is fixed.

Dependencies and integration: integrates with HDFS protocol `LocatedBlock` and read/status code that needs block length metadata.

Risks and test signals: message constructors include the block and optional file path, improving diagnostics. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/CannotObtainBlockLengthException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ClientContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ClientContext.java

Purpose: private shared client context for `DFSClient` instances, allowing socket, short-circuit, key provider, byte-array, dead-node, and located-block-refresh resources to be reused by context name.

Important APIs and functions: static `get()`/`getFromConf()` manage a global `CACHES` map; constructor initializes arrays of `ShortCircuitCache`, `PeerCache`, `DomainSocketFactory`, `KeyProviderCache`, `ByteArrayManager`, topology resolution, dead-node and located-block-refresher flags. Accessors expose caches and settings. `reference()` starts optional `DeadNodeDetector` and `LocatedBlocksRefresher`; `unreference()` shuts them down when the reference count reaches zero.

Control flow: `get()` synchronizes on `ClientContext.class`, creates or reuses contexts, prints a one-time warning on short-circuit config mismatch, then increments the instance reference count. Network distance either uses resolved rack topology or falls back to local-address check versus `Integer.MAX_VALUE`.

State and persistence: global static cache persists contexts for the JVM lifetime unless not externally cleared. Instance mutable state includes warning flag, reference counter, optional detector/refresher threads, and legacy block reader disable flag.

Dependencies and integration: integrates `DfsClientConf`, short-circuit cache, peer cache, key provider cache, domain sockets, network topology mapping, dead-node detection, located-block refresh, and DFS utility address checks.

Risks and test signals: global caching can reuse a context with incompatible later configuration, only warning once. Reference/unreference correctness is important to avoid background thread leaks. `getShortCircuitCache(long)` modulo depends on positive configured cache count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ClientContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ClientGSIContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ClientGSIContext.java

Purpose: client-side `AlignmentContext` implementation for global state ID propagation in RPC headers, including router federated state for Router-Based Federation.

Important APIs and functions: stores a `LongAccumulator` tracking max last-seen state ID and optional `routerFederatedState` `ByteString`. `receiveResponseState()` merges response state; `updateRequestState()` writes state into outbound request headers; static `getRouterFederatedStateMap()` parses `RouterFederatedStateProto`; `mergeRouterFederatedState()` keeps the max state ID per namespace.

Control flow: response handling prefers router federated state if present; otherwise it accumulates plain `stateId`. Request handling emits plain state ID only after the accumulator has moved from `Long.MIN_VALUE`, and emits federated state when present. Server-side methods are unsupported or no-op on the client.

State and persistence: state is in-memory per client context. `receiveResponseState()` and `updateRequestState()` are synchronized for the federated state field; the accumulator is thread-safe.

Dependencies and integration: integrates IPC alignment headers, generated HDFS protobufs, and protobuf `ByteString`.

Risks and test signals: invalid federated state bytes are silently treated as empty maps, which favors robustness but can hide corrupt state. Merge defaults missing namespace values to zero, so negative namespace state IDs would be normalized upward if ever introduced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ClientGSIContext.java -->
