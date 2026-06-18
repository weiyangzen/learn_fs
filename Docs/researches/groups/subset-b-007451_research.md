# Research: subset-b-007451

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/resources/hdfs-rbf-default.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/resources/hdfs-rbf-default.xml

This XML file is the default configuration catalog for HDFS Router-Based Federation (RBF). It is not runtime code, but it is a central integration contract: `RBFConfigKeys` and the Router services consume these keys unless an operator overrides them in `hdfs-rbf-site.xml`.

Important configuration areas are Router identity and default nameservice selection, RPC/admin/HTTP service enablement and bind addresses, synchronous and asynchronous RPC handler sizing, downstream connection-pool behavior, metrics/JMX reporting, state-store driver and serializer selection, cache TTLs, router and namenode heartbeat intervals, safemode behavior, mount-table caching, quota management, client retry/partial-listing behavior, Kerberos/SPNEGO/keytab settings, delegation-token secret manager implementation, fairness policy controller permits, cross-namespace federation rename options, observer-read propagation, and async file/filesystem state-store driver threads.

State and persistence behavior is defined through the state-store defaults: ZooKeeper is the default state-store backend, with file, filesystem, and MySQL alternatives described; membership and router records have expiration and optional deletion windows; mount table and quota state are cached inside Routers and refreshed on TTLs or optional refresh-service calls. The file also controls when Routers heartbeat themselves, monitor namenodes, and enter safemode if state-store reachability is lost.

Dependencies are mostly class-name strings that bind this resource to Java implementations such as `MountTableResolver`, `MembershipNamenodeResolver`, `StateStoreSerializerPBImpl`, `StateStoreZooKeeperImpl`, `ZKDelegationTokenSecretManagerImpl`, and `NoRouterRpcFairnessPolicyController`.

Risks are configuration drift and invalid defaults. The file contains a duplicated `dfs.federation.router.async.rpc.responder.count` property and an apparent extra `<property>` opening near the datanode-report cache section, so consumers and XML validation tests need to catch parse and duplicate-key issues. The test signal should include config-field coverage tests, XML parse validation, and targeted Router startup tests for RPC, state-store, security, fairness, and observer-read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/resources/hdfs-rbf-default.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/webapps/proto-web.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/webapps/proto-web.xml

This is the minimal servlet deployment descriptor for the RBF web application resources. It declares a Servlet 2.4 `<web-app>` root and no explicit servlets, filters, listeners, welcome files, or security constraints. The purpose is packaging: it gives the Router webapp a valid descriptor while the actual Hadoop HTTP server and web resources are wired by the surrounding HDFS web framework.

There are no APIs, functions, stateful classes, or persistence mechanisms in this file. Control flow is entirely container-driven: the webapp descriptor is read by the embedded servlet container when the Router HTTP server starts, then static resources and framework-provided endpoints are served according to Hadoop's HTTP server configuration.

Its dependencies are the Java EE XML namespace and the Hadoop build/webapp packaging path. Integration points include the Router HTTP/HTTPS addresses from `hdfs-rbf-default.xml`, the static JavaScript files in `src/main/webapps/router`, and framework endpoints such as `/jmx`, `/conf`, and `/webhdfs/v1`.

The main risk is assuming this descriptor enforces security or endpoint mappings. It does not; SPNEGO, HTTPS, filters, and WebHDFS/JMX exposure are configured elsewhere. Test signals are packaging/startup tests that verify the Router web UI can load and that web resources are reachable through the configured Router HTTP server.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/webapps/proto-web.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/webapps/router/explorer.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/webapps/router/explorer.js

This browser-side module implements the Router web file explorer. It uses jQuery, Bootstrap modals/popovers, Dust templates, DataTables, Moment, and WebHDFS endpoints to browse directories, inspect files, edit metadata, create directories, upload files, delete paths, and move selected files.

Important functions include `browse_directory`, which calls `/webhdfs/v1/<path>?op=LISTSTATUS`, renders the `explorer` Dust template, wires row handlers, and initializes DataTables; `view_file_details`, which calls `GET_BLOCK_LOCATIONS`, renders block details, and performs `OPEN` preview reads through `noredirect=true`; `delete_path`, `set_permissions`, and `makeEditable`, which issue WebHDFS `DELETE`, `SETPERMISSION`, `SETOWNER`, and `SETREPLICATION` calls; upload logic, which performs two-step WebHDFS `CREATE` with a redirected datanode write; and cut/paste logic, which stores selected filenames in `sessionStorage` and issues `RENAME`.

Control flow is hash-driven. A `hashchange` listener normalizes the current path and calls `browse_directory`; UI event handlers then mutate HDFS state and reload the current directory. State is mostly DOM state plus `current_directory` and `sessionStorage` entries for pending move operations. No durable client-side persistence is used beyond session storage.

Integration points are the Router WebHDFS proxy, `/conf` for umask discovery, Dust templates embedded in the page, Bootstrap modals, and the datanode redirect locations returned by WebHDFS. Risks include synchronous AJAX calls during preview and config lookup, HTML injection exposure because server-supplied messages and Dust output are inserted into the DOM, event-handler accumulation on repeated modal opens if handlers are not cleared everywhere, and WebHDFS behavior differences across secure/non-secure clusters. Test signals should include browser/UI tests or WebHDFS integration tests for listing, upload, delete, permission edits, rename, error handling for 401/403/404, IPv6/encoded paths, and large-file preview.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/webapps/router/explorer.js -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/webapps/router/federationhealth.js -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/webapps/router/federationhealth.js

This browser-side module renders the Router federation health dashboard. It loads Router and NameNode JMX beans, normalizes JSON fields that arrive as serialized strings, renders Dust templates for each tab, and initializes DataTables and a D3 datanode usage histogram.

Important functions are `load_overview`, `load_namenode_info`, `load_router_info`, `load_datanode_info`, and `load_mount_table`. They fetch JMX endpoints such as `Hadoop:service=Router,name=FederationState`, `Hadoop:service=Router,name=Router`, `java.lang:type=Memory`, and `Hadoop:service=NameNode,name=NameNodeInfo`. Helper functions convert timestamp fields, classify Router/NameNode state into icon/status labels, parse mount-table read-only and fault-tolerant fields, derive datanode web URLs from info addresses, and render usage bars/histograms. `load_page` dispatches based on the location hash.

State is transient DOM state, `window.liveNodes` for histogram click behavior, and parsed copies of JMX payloads. Persistence lives outside the UI in Router JMX/state-store data; this script only presents it. Dependencies include jQuery, Dust, DataTables, Moment, D3, and Hadoop's `load_json` helper.

Integration points are the Router metrics MBeans and federation state structures: `Nameservices`, `Namenodes`, `Routers`, `MountTable`, and datanode maps must remain parseable JSON strings. Risks include fragile parsing of non-standard JMX string fields, TypeError masking in `guard_with_startup_progress`, global state pollution via `window.liveNodes`, and stale UI assumptions when Router status enums or JMX field names change. Test signals should cover each tab against representative JMX fixtures, router safemode/startup states, unavailable namenodes, disabled nameservices, mount-table status formatting, and datanode address parsing for IPv4/IPv6 and HTTPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/webapps/router/federationhealth.js -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/site/site.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/site/site.xml

This Maven site descriptor defines the generated site skin and a single external Hadoop link for the `hadoop-hdfs-rbf` module. It is build metadata rather than runtime code.

The only meaningful elements are the project name, `maven-stylus-skin` dependency using `${maven-stylus-skin.version}`, and the body link to `http://hadoop.apache.org/`. There are no functions, classes, runtime state, persistence behavior, or direct production dependencies.

Integration is through Maven site generation. The descriptor affects documentation output for the module, not Router behavior, tests, or packaged services. Its risk surface is small: bad skin coordinates or a stale HTTP link can break or degrade generated docs, but cannot affect HDFS runtime. Test signals are Maven site-generation checks and link validation if documentation publishing is part of CI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/site/site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/RouterHDFSContract.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/RouterHDFSContract.java

`RouterHDFSContract` adapts Hadoop's generic `HDFSContract` to a Router-Based Federation mini cluster. It supplies the `FileSystem` under test for the many `AbstractContract*Test` subclasses in this package.

Important APIs are the static lifecycle methods `createCluster()`, `createCluster(boolean security)`, `createCluster(boolean ha, int numNameServices, boolean security)`, `destroyCluster()`, `getCluster()`, `getRouterCluster()`, and `getFileSystem()`, plus the override `getTestFileSystem()`. `BLOCK_SIZE` is tied to `AbstractFSContractTestBase.TEST_FILE_LEN`.

Control flow creates optional secure configuration through `SecurityConfUtil`, builds a `MiniRouterDFSCluster`, starts namenodes/datanodes, starts routers, registers namenodes with all routers, installs mock mount locations, transitions one namenode per nameservice active in HA mode, and waits for active namespace discovery. Teardown shuts the cluster down and destroys the security context.

State is a static `MiniRouterDFSCluster`, so tests rely on class-level setup/teardown isolation. Dependencies include `MiniDFSCluster`, `MiniRouterDFSCluster`, `SecurityConfUtil`, JUnit assertions, and federation test constants. Integration points are Router RPC clients and mock mount-table resolution. Risks are static-state leakage between contract suites, partial startup cleanup, random router selection hiding per-router issues, and security context cleanup failures. Test signals are all RPC contract subclasses that instantiate this contract in secure and non-secure modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/RouterHDFSContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/SecurityConfUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/SecurityConfUtil.java

`SecurityConfUtil` centralizes Kerberos, HTTPS, block-token, and delegation-token setup for secure Router contract tests. It is a test utility with only static methods and process-local static state.

`initSecurity()` deletes and recreates a test directory, starts `MiniKdc`, creates SPNEGO and router principals in a shared keytab, enables Kerberos authentication in an `HdfsConfiguration`, configures NN/DN and Router principals/keytabs, enables block access tokens and authenticated data transfer, sets HTTPS-only HTTP policy, creates SSL keystore resources through `KeyStoreTestUtil`, uses `StateStoreFileImpl` for the state store, binds Router RPC to localhost, and installs `MockDelegationTokenSecretManager` as the router delegation-token driver. `destroy()` stops the KDC, deletes the base directory, and cleans SSL config.

State and persistence include static paths for keystore and SSL configuration, a static `MiniKdc`, and generated keytab/keystore files under the JUnit test directory. Dependencies include MiniKdc, UGI, SecurityUtil, DFS/RBF config keys, `StateStoreDriver`, and mock federation security classes.

The main risks are global UGI/security-mode mutation, cleanup not resetting static fields after KDC shutdown, platform-specific hostname behavior handled by the Windows localhost branch, and secure tests sharing one router identity for NN, DN, and Router roles. Test signals are all `*Secure` Router contract tests plus the delegation-token contract test, which exercise Kerberos startup, HTTPS configuration, block tokens, and router delegation-token wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/SecurityConfUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractAppend.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractAppend.java

This test class runs Hadoop's shared `AbstractContractAppendTest` suite against the Router RPC `FileSystem`. It provides no local test methods; inherited contract tests drive append behavior.

`@BeforeAll createCluster()` starts a non-secure HA federated Router cluster through `RouterHDFSContract.createCluster()`. `@AfterAll teardownCluster()` destroys it. `createContract(Configuration)` returns a new `RouterHDFSContract`, which supplies a random Router-backed `DistributedFileSystem`.

State is class-level mini-cluster state owned by `RouterHDFSContract`. Dependencies are JUnit 5 lifecycle annotations and the Hadoop FS contract framework. Integration points are Router RPC append forwarding, mock mount locations, active nameservice discovery, and HDFS append semantics behind the router.

Risks are mostly inherited: append tests can pass through one random router while another router is broken, and static cluster reuse means teardown failures affect later suites. The test signal is coverage that Router RPC preserves HDFS append contract behavior in a non-secure federated cluster.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractAppend.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractAppendSecure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractAppendSecure.java

This class runs the inherited append contract suite over a secure Router RPC cluster. It is structurally identical to the non-secure append test, but calls `RouterHDFSContract.createCluster(true)`.

The lifecycle delegates to `RouterHDFSContract` and `SecurityConfUtil`: MiniKdc, HTTPS-only DFS HTTP policy, block access tokens, authenticated data transfer, Router principals, and mock delegation-token manager are initialized before inherited append operations run. The contract factory returns `RouterHDFSContract`.

State is the static federated mini cluster plus process-wide UGI Kerberos state. Dependencies are JUnit 5, `AbstractContractAppendTest`, `RouterHDFSContract`, and `SecurityConfUtil`.

The key integration signal is that Router RPC append behavior works when Hadoop security is enabled. Risks include MiniKdc flakiness, global security settings affecting adjacent tests, and inherited append cases not explicitly checking every token-renewal path. This test is valuable because append combines write pipeline behavior with authentication and block tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractAppendSecure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractConcat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractConcat.java

This class runs `AbstractContractConcatTest` against a non-secure Router RPC filesystem. It verifies that concat operations routed through RBF still satisfy HDFS contract expectations.

The setup starts the standard non-secure Router cluster, then performs a simple `getDefaultBlockSize(new Path("/"))` call through the Router-backed filesystem as an early readiness check. Teardown destroys the static cluster, and `createContract` returns `RouterHDFSContract`.

State and persistence are inherited from the mini HDFS cluster and mock mount mappings. Dependencies include `Path`, JUnit lifecycle annotations, and the HDFS contract framework.

Integration points are Router RPC concat forwarding, block-size metadata lookup, and active nameservice routing. Risks include concat restrictions around block sizes and same-filesystem constraints being tested only through inherited scenarios, and readiness being sampled through a random router. The test signal is non-secure Router compatibility with HDFS concat semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractConcat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractConcatSecure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractConcatSecure.java

This secure variant runs `AbstractContractConcatTest` through a Kerberized Router RPC cluster. It starts the cluster with `RouterHDFSContract.createCluster(true)` and performs the same default-block-size readiness probe as the non-secure variant.

Control flow is class-level setup, inherited concat cases, and class-level teardown. State includes the static `MiniRouterDFSCluster`, MiniKdc artifacts, SSL configuration, and UGI security mode initialized by `SecurityConfUtil`. The contract factory returns `RouterHDFSContract`.

Dependencies are the Hadoop FS contract framework, Router security test utility, and the secure mini HDFS stack. Integration points are Router RPC concat, downstream namenode auth, block-token behavior, and mount resolution.

Risks include Kerberos/HTTPS fixture cost and inherited concat tests not covering all cross-nameservice rename/copy variants. Its test signal is that concat remains compatible with Router forwarding when secure authentication and block access controls are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractConcatSecure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractCreate.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractCreate.java

This class runs `AbstractContractCreateTest` against the non-secure Router RPC filesystem. It validates inherited file creation behavior such as overwrite, parent handling, stream semantics, and metadata expectations through RBF.

Setup starts the standard two-nameservice HA `MiniRouterDFSCluster` via `RouterHDFSContract.createCluster()`. Teardown calls `RouterHDFSContract.destroyCluster()`. `createContract` returns `RouterHDFSContract`.

State lives in the static mini cluster, its mock mount locations, and the files/directories created by inherited tests. Dependencies are JUnit 5 lifecycle hooks and Hadoop's contract test base.

Integration points are Router RPC create forwarding, mount-table path resolution, active namenode selection, and HDFS write pipeline creation behind the Router. Risks include random-router coverage gaps and inherited tests mainly validating general HDFS semantics rather than Router-specific multi-destination edge cases. The test signal is baseline non-secure create compatibility for Router-backed HDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractCreate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractCreateSecure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractCreateSecure.java

This class runs `AbstractContractCreateTest` over a secure Router RPC filesystem. Its setup calls `RouterHDFSContract.createCluster(true)`, enabling the Kerberos and HTTPS settings from `SecurityConfUtil`.

Inherited test methods perform the actual create-contract assertions. The only local API is `createContract(Configuration)`, which returns a `RouterHDFSContract`. Teardown destroys both the mini cluster and security context.

State includes MiniKdc, generated keytabs/keystores, UGI global security configuration, router/namenode/datanode mini-cluster state, and files created by inherited tests. Dependencies are JUnit, `AbstractContractCreateTest`, and the secure Router contract harness.

The integration signal is that authenticated clients can create files through the Router and receive normal HDFS behavior. Risks include fixture flakiness, static security state leaking, and limited Router-specific assertions around delegation-token or per-nameservice authorization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractCreateSecure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractDelegationToken.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractDelegationToken.java

This class extends `AbstractContractGetFileStatusTest` but adds an explicit secure Router delegation-token test. It starts a secure Router cluster, returns `RouterHDFSContract` from `createContract`, and destroys the cluster afterward.

The local `testRouterDelegationToken()` obtains the Router-backed `FileSystem`, casts it to `DistributedFileSystem`, calls `getDelegationToken(SecurityConfUtil.getRouterUserName())`, and asserts that the token is not null. This checks that the Router's configured delegation-token secret manager can issue tokens to DFS clients in the secure contract environment.

State includes the secure mini cluster, mock delegation-token manager, KDC artifacts, and the DFS client token cache. Dependencies include `DistributedFileSystem`, Hadoop security `Token`, `DelegationTokenIdentifier`, JUnit assertions, and `SecurityConfUtil`.

Integration points are Router RPC security, the RBF secret-manager configuration, DFS client token APIs, and Kerberos login context. Risks include only checking token issuance, not renewal/cancel or persistence across Router restarts; it also relies on a mock secret manager rather than the default ZooKeeper implementation. Test signal is a direct smoke test for secure Router delegation-token availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractDelegationToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractDelete.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractDelete.java

This class adapts `AbstractContractDeleteTest` to non-secure Router RPC. The inherited contract methods validate delete semantics through the Router, including recursive and non-recursive behavior where covered by the base suite.

Setup and teardown are standard `RouterHDFSContract.createCluster()` and `destroyCluster()`. `createContract` returns a new `RouterHDFSContract`.

State is the class-level mini federated cluster and test-created filesystem entries. Dependencies are the Hadoop contract test framework and JUnit 5. Integration points are Router path resolution, downstream namenode delete RPCs, mount-point behavior, and HDFS error propagation.

Risks include inherited tests not fully exercising deletes across multiple mounted namespaces and random router selection masking router-local cache problems. The test signal is baseline non-secure delete compatibility through RBF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractDeleteSecure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractDeleteSecure.java

This secure variant runs `AbstractContractDeleteTest` through a Kerberized Router RPC cluster. It differs from the non-secure class only by calling `RouterHDFSContract.createCluster(true)`.

Control flow is class setup, inherited delete tests, and teardown. State includes the secure mini HDFS/RBF cluster, KDC and SSL artifacts, UGI security mode, mock state-store/delegation-token settings, and inherited test paths.

Dependencies are JUnit 5, Hadoop FS contract tests, `RouterHDFSContract`, and `SecurityConfUtil`. Integration points are authenticated Router RPC delete calls and downstream namenode authorization.

Risks are secure fixture cost and global security-state leakage; inherited delete tests may not cover all read-only mount or cross-namespace delete semantics. The test signal confirms secure Router delete behavior follows the HDFS contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractDeleteSecure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractGetFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractGetFileStatus.java

This class runs `AbstractContractGetFileStatusTest` over a non-secure Router RPC filesystem. It validates inherited file-status behavior such as metadata lookup, nonexistent paths, directory/file distinctions, and permission/ownership reporting as exposed through the Router.

The local code is only lifecycle and contract construction: `createCluster()`, `teardownCluster()`, and `createContract(Configuration)`. Cluster setup uses the standard non-secure `RouterHDFSContract` path.

State is the static mini cluster and HDFS metadata created by inherited tests. Dependencies are JUnit 5 and the Hadoop contract framework. Integration points are Router `getFileInfo`/status forwarding, mock mount resolution, and active namenode selection.

Risks include limited direct assertions for mount-table entries at root and random-router selection. The test signal is baseline status/metadata compatibility for non-secure RBF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractGetFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractGetFileStatusSecure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractGetFileStatusSecure.java

This class runs `AbstractContractGetFileStatusTest` through a secure Router RPC cluster. Setup uses `RouterHDFSContract.createCluster(true)` so inherited status tests execute with Kerberos, HTTPS-only HTTP policy, block tokens, and mock Router delegation-token support.

The contract factory returns `RouterHDFSContract`; teardown destroys the static cluster and security context. No local test methods override the inherited metadata suite.

State includes secure mini-cluster metadata, UGI security configuration, generated keytabs/keystores, and files/directories created by inherited tests. Dependencies are JUnit, Hadoop contract tests, and the secure Router harness.

Integration points are authenticated status RPCs, Router-to-namenode metadata forwarding, and permission/ownership visibility under security. Risks include global security state leakage and inherited coverage not checking every Router-specific federation state. The test signal is secure metadata lookup compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractGetFileStatusSecure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractMkdir.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractMkdir.java

This class runs `AbstractContractMkdirTest` against a non-secure Router RPC filesystem. Inherited tests verify directory creation, parent handling, idempotency, and error behavior as implemented through the Router.

Setup starts the standard federated Router cluster, teardown destroys it, and `createContract` returns `RouterHDFSContract`. No local test methods change the inherited suite.

State is the static `MiniRouterDFSCluster` plus directories created by the base tests. Dependencies are JUnit 5 and Hadoop FS contract classes. Integration points are Router path resolution, downstream namenode `mkdirs`, and mock mount locations.

Risks include limited coverage of namespace-boundary directory creation and root mount behavior beyond inherited tests. The test signal is non-secure Router directory-creation contract compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractMkdir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractMkdirSecure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractMkdirSecure.java

This secure variant runs `AbstractContractMkdirTest` against a Kerberized Router RPC filesystem. It delegates setup to `RouterHDFSContract.createCluster(true)` and teardown to `destroyCluster()`.

Inherited tests perform the directory behavior assertions. The contract factory returns `RouterHDFSContract`, so all operations route through a random Router RPC endpoint.

State includes MiniKdc artifacts, UGI security mode, Router and namenode keytab settings, SSL config, and test-created directories. Dependencies are JUnit, the Hadoop contract suite, and `SecurityConfUtil` through `RouterHDFSContract`.

Integration points are secure Router RPC `mkdirs`, downstream namenode authentication, and mount-table resolution. Risks are fixture flakiness and inherited tests not covering all permission-denied cases specific to RBF. Test signal is secure directory operation compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractMkdirSecure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractOpen.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractOpen.java

This class runs `AbstractContractOpenTest` through a non-secure Router RPC filesystem. It validates inherited open/read behavior, including file reads and expected exceptions for invalid open operations where the base suite defines them.

Setup starts a standard `RouterHDFSContract` cluster. Teardown destroys it. `createContract(Configuration)` returns `RouterHDFSContract`.

State is test-file data in the mini HDFS cluster and static Router cluster state. Dependencies are JUnit and the Hadoop contract framework. Integration points are Router open forwarding, block location/read pipeline setup, mount resolution, and active namenode selection.

Risks include random-router selection and inherited read tests not explicitly stressing observer reads, failover, or stale router caches. The test signal is baseline non-secure open/read compatibility for Router-backed HDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractOpen.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractOpenSecure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractOpenSecure.java

This secure variant runs `AbstractContractOpenTest` against a Kerberized Router RPC filesystem. It calls `RouterHDFSContract.createCluster(true)` and otherwise inherits all open/read test logic.

The contract factory returns `RouterHDFSContract`; teardown releases the mini cluster and security context. State includes secure mini-cluster data, generated keytabs and SSL config, UGI state, and inherited test files.

Dependencies include the Hadoop contract suite, `SecurityConfUtil`, MiniKdc, and Router RPC clients. Integration points are secure open/read forwarding, block-token-enabled data reads, and authenticated Router-to-namenode access.

Risks include secure test flakiness and insufficient direct coverage for token expiration or WebHDFS read differences. The test signal is that standard file open/read contract behavior works through a secure Router RPC endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractOpenSecure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRename.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRename.java

This class runs `AbstractContractRenameTest` over a non-secure Router RPC filesystem. It verifies inherited rename behavior through RBF, including file and directory rename cases covered by the base contract suite.

Setup and teardown use `RouterHDFSContract.createCluster()` and `destroyCluster()`. `createContract` returns a Router HDFS contract.

State is class-level mini-cluster state plus filesystem entries created during inherited rename tests. Dependencies are JUnit and the Hadoop contract framework. Integration points are Router rename forwarding, path resolution through mock mount locations, active namenode selection, and HDFS rename semantics.

Risks include inherited tests generally covering same-filesystem renames, while RBF has additional cross-nameservice rename behavior configured separately by federation rename options. Random Router selection may miss per-router cache issues. The test signal is baseline non-secure rename compatibility through Router RPC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRename.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRenameSecure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRenameSecure.java

This secure variant runs `AbstractContractRenameTest` over a Kerberized Router RPC filesystem. It initializes the secure cluster with `RouterHDFSContract.createCluster(true)` and returns `RouterHDFSContract` from the contract factory.

State includes static Router cluster state, MiniKdc, generated keytabs/keystores, secure UGI settings, and test paths. Dependencies include the Hadoop contract suite, JUnit, and `SecurityConfUtil`.

Integration points are authenticated Router rename RPCs, downstream namenode permission checks, and mount-table path resolution. Risks are similar to the non-secure rename class plus secure fixture leakage; it does not directly exercise the federation rename DistCp procedure or cross-nameservice policy options. The signal is secure baseline rename compatibility through Router RPC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRenameSecure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRootDirectory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRootDirectory.java

This class adapts `AbstractContractRootDirectoryTest` to the non-secure Router RPC filesystem. It starts the standard Router cluster and returns `RouterHDFSContract`, but overrides several inherited root-directory tests as no-ops.

The disabled methods are `testListEmptyRootDirectory`, `testRmEmptyRootDirNonRecursive`, `testRecursiveRootListing`, `testRmRootRecursive`, and `testRmEmptyRootDirRecursive`. The reason is that the Router root contains mount points, so generic assumptions about an empty root or deleting root do not apply to RBF.

State is the mini federation root mapping installed by `MiniRouterDFSCluster.installMockLocations()`. Dependencies are JUnit lifecycle hooks and the base contract suite. Integration points are Router root listing and mount-point semantics.

The main risk is reduced coverage for root behavior; disabling tests is appropriate for RBF but can hide regressions in root listing/deletion protections unless covered elsewhere. The test signal is explicit documentation that generic root-directory expectations differ for Router federation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRootDirectory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRootDirectorySecure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRootDirectorySecure.java

This secure root-directory contract class mirrors the non-secure Router root test but starts the Kerberized cluster with `RouterHDFSContract.createCluster(true)`.

It returns `RouterHDFSContract` from `createContract` and disables inherited root tests that assume an empty or removable root: empty-root listing, non-recursive root removal, recursive root listing, recursive root removal, and empty-root recursive removal. Those cases do not apply because the Router root exposes federation mount points.

State includes the secure mini-cluster, KDC/SSL artifacts, and Router mount mappings. Dependencies are JUnit, Hadoop root-directory contract tests, and `SecurityConfUtil`.

Integration points are secure Router root listing and mount-point behavior. Risks include losing security-specific root assertions when inherited tests are no-oped, so separate Router-specific tests should cover permission and listing behavior at root. The test signal documents that secure RBF also intentionally diverges from generic empty-root assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractRootDirectorySecure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSeek.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSeek.java

This class runs `AbstractContractSeekTest` against a non-secure Router RPC filesystem. It validates inherited seek/read behavior through RBF.

Setup starts the normal Router cluster; teardown destroys it. The contract factory returns `RouterHDFSContract`. No inherited seek cases are disabled in the RPC variant.

State is the mini HDFS cluster and test files created by the seek contract suite. Dependencies include JUnit and Hadoop FS contract classes. Integration points are Router open/read forwarding, DFS input stream behavior, block locations, and active namenode routing.

Risks include random-router selection and lack of direct failover/observer-read coverage, but this class gives useful regression coverage for standard seek semantics through Router RPC. The test signal is non-secure seek compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSeek.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSeekSecure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSeekSecure.java

This secure variant runs `AbstractContractSeekTest` over a Kerberized Router RPC filesystem. It starts the secure cluster with `RouterHDFSContract.createCluster(true)` and returns `RouterHDFSContract`.

Inherited tests perform seek behavior assertions. State includes secure mini-cluster files, KDC state, SSL config, UGI security settings, and Router mount mappings.

Dependencies are the FS contract framework, JUnit, Router cluster harness, and MiniKdc-backed security utility. Integration points are authenticated file open/read/seek operations and block-token-enabled data access behind the Router.

Risks are secure fixture flakiness and limited coverage of token lifecycle during long reads. The test signal is secure seek/read compatibility for Router RPC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSeekSecure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSetTimes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSetTimes.java

This class runs `AbstractContractSetTimesTest` against a non-secure Router RPC filesystem. The inherited suite checks modification/access time updates and expected metadata behavior.

The local code follows the standard contract adapter pattern: class-level Router cluster startup, class-level teardown, and `createContract(Configuration)` returning `RouterHDFSContract`.

State is filesystem metadata in the mini HDFS cluster and static Router cluster state. Dependencies are JUnit and Hadoop contract tests. Integration points are Router RPC forwarding for `setTimes`, status reads after mutation, and mount resolution.

Risks include inherited tests not covering all federation cache-refresh edge cases or multiple routers observing the changed metadata. The test signal is baseline non-secure timestamp mutation compatibility through RBF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSetTimes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSetTimesSecure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSetTimesSecure.java

This secure variant runs `AbstractContractSetTimesTest` over a Kerberized Router RPC filesystem. Setup calls `RouterHDFSContract.createCluster(true)` and teardown destroys the cluster/security context.

Inherited tests perform the timestamp behavior checks. The contract factory returns `RouterHDFSContract`.

State includes secure mini-cluster metadata, generated security artifacts, UGI state, and Router mount mappings. Dependencies are JUnit, Hadoop FS contract classes, and the secure Router contract harness.

Integration points are authenticated `setTimes` forwarding, downstream namenode permission checks, and status reads through the Router. Risks include fixture leakage and limited explicit coverage for cache propagation across multiple routers. The test signal is secure timestamp mutation compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/TestRouterHDFSContractSetTimesSecure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/RouterWebHDFSContract.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/RouterWebHDFSContract.java

`RouterWebHDFSContract` adapts Hadoop's `HDFSContract` to a Router WebHDFS endpoint. It is the shared contract factory for the WebHDFS Router tests.

Important APIs are `createCluster()`, `createCluster(Configuration)`, `destroyCluster()`, `getCluster()`, `getFileSystem()`, `getTestFileSystem()`, and `getScheme()`. The constructor adds `contract/webhdfs.xml` to the inherited HDFS contract configuration.

Control flow starts an HA two-nameservice `MiniRouterDFSCluster`, switches to independent datanodes, sets three datanodes per nameservice, starts the cluster and routers, registers namenodes, installs mock mount locations, transitions one namenode active per nameservice, and waits for active namespaces. `getFileSystem()` builds a `webhdfs://<router-http-address>` URI from a random `RouterContext` and creates a WebHDFS `FileSystem`.

State is a static `MiniRouterDFSCluster`; no secure setup is included. Dependencies include `WebHdfsConstants`, `WebHdfsFileSystem`, `MiniRouterDFSCluster`, and JUnit assertions. Integration points are Router HTTP/WebHDFS, mock mount resolution, and the contract webhdfs XML. Risks include returning null on URI syntax errors, random router selection, and using only non-secure WebHDFS. Test signal is shared by all WebHDFS Router contract subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/RouterWebHDFSContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractAppend.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractAppend.java

This class runs `AbstractContractAppendTest` against the Router WebHDFS filesystem. It starts the WebHDFS Router contract cluster, destroys it afterward, and returns `RouterWebHDFSContract`.

The inherited suite performs append behavior checks through `webhdfs://<router-http-address>`, not direct Router RPC. State is the static WebHDFS mini cluster and files created by inherited tests. Dependencies include JUnit, Hadoop contract tests, and WebHDFS client classes through the contract.

Integration points are Router HTTP service, WebHDFS operation translation, mount resolution, and downstream HDFS append. Risks include WebHDFS-specific redirect behavior and lack of secure WebHDFS coverage here. The test signal is non-secure append compatibility via Router WebHDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractAppend.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractConcat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractConcat.java

This class runs `AbstractContractConcatTest` through Router WebHDFS. Setup starts `RouterWebHDFSContract.createCluster()` and performs a `getDefaultBlockSize(new Path("/"))` readiness probe through the WebHDFS filesystem.

The contract factory returns `RouterWebHDFSContract`; teardown destroys the static cluster. State is WebHDFS mini-cluster state and inherited test files. Dependencies are JUnit, `Path`, Hadoop contract tests, and Router WebHDFS.

Integration points are WebHDFS concat support, Router HTTP handling, redirect behavior, and downstream namenode concat. Risks include WebHDFS API differences from RPC and inherited tests not covering cross-nameservice concat constraints. The signal is non-secure Router WebHDFS concat contract compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractConcat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractCreate.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractCreate.java

This class runs `AbstractContractCreateTest` against Router WebHDFS. It starts the WebHDFS Router mini cluster, returns `RouterWebHDFSContract`, and destroys the cluster after inherited tests finish.

State is the static WebHDFS contract cluster, independent datanodes, mock mount mappings, and files created by the base suite. Dependencies are JUnit and Hadoop contract tests.

Integration points are WebHDFS `CREATE` handling through the Router HTTP server, datanode write redirects, mount resolution, and HDFS create semantics. Risks include redirect and permission behavior differing from RPC tests, and no secure SPNEGO WebHDFS variant in this subset. The test signal is baseline create compatibility for Router WebHDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractCreate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractDelete.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractDelete.java

This class runs `AbstractContractDeleteTest` over Router WebHDFS. It delegates setup/teardown to `RouterWebHDFSContract` and returns that contract from `createContract`.

Inherited tests issue delete operations through the WebHDFS client and Router HTTP service. State is mini-cluster file state and static contract state. Dependencies are JUnit, Hadoop contract tests, and Router WebHDFS client integration.

Integration points are WebHDFS `DELETE`, Router mount resolution, downstream namenode deletion, and error propagation over HTTP. Risks include HTTP status mapping differences versus RPC exceptions and missing secure WebHDFS coverage. The test signal is non-secure delete compatibility via Router WebHDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractMkdir.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractMkdir.java

This class runs `AbstractContractMkdirTest` through Router WebHDFS. Setup starts the non-secure WebHDFS Router cluster and teardown destroys it.

The only local behavior is `createContract(Configuration)`, returning `RouterWebHDFSContract`. Inherited tests drive WebHDFS `MKDIRS` behavior through the Router HTTP endpoint.

State is the static mini cluster and created directory metadata. Dependencies are JUnit, Hadoop contract tests, and Router WebHDFS. Integration points are WebHDFS directory operations, Router HTTP service, mount table resolution, and downstream HDFS directory creation.

Risks include HTTP-specific error mapping and lack of secure coverage. The test signal is non-secure mkdir compatibility via Router WebHDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractMkdir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractOpen.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractOpen.java

This class runs most of `AbstractContractOpenTest` through Router WebHDFS, but overrides two inherited directory-open tests as no-ops.

Setup and teardown use `RouterWebHDFSContract`. `createContract` returns the WebHDFS contract. `testOpenReadDir()` and `testOpenReadDirWithChild()` are intentionally empty because WebHDFS itself allows open-read on directories, so the generic contract expectation does not hold.

State is WebHDFS mini-cluster file state and static cluster state. Dependencies are JUnit, the Hadoop open contract suite, and Router WebHDFS. Integration points are WebHDFS `OPEN`, datanode read redirects, Router path resolution, and downstream HDFS reads.

Risks include reduced coverage for directory-open error behavior and WebHDFS-specific behavior diverging from RPC. The test signal is file-open compatibility through Router WebHDFS while documenting inherited cases that do not apply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractOpen.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractRename.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractRename.java

This class runs `AbstractContractRenameTest` against Router WebHDFS. It delegates lifecycle to `RouterWebHDFSContract` and returns that contract.

Inherited tests issue WebHDFS rename operations through the Router HTTP endpoint. State is the static WebHDFS mini cluster and test paths. Dependencies are JUnit and Hadoop contract tests.

Integration points are WebHDFS `RENAME`, Router mount resolution, downstream namenode rename, and HTTP error/result translation. Risks include inherited tests not exercising RBF cross-nameservice federation rename behavior and no secure WebHDFS variant. The signal is baseline non-secure rename compatibility for Router WebHDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractRename.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractRootDirectory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractRootDirectory.java

This WebHDFS root-directory contract class adapts `AbstractContractRootDirectoryTest` to Router federation and disables generic root assumptions that do not apply.

Lifecycle uses `RouterWebHDFSContract`; `createContract` returns the WebHDFS contract. It no-ops empty root listing, non-recursive root removal, recursive root listing, recursive root removal, empty-root recursive removal, and `testSimpleRootListing`. Comments explain that Router root contains mount points and DFSRouter does not support `LISTSTATUS_BATCH`.

State is the Router WebHDFS mini cluster and mock root mount mapping. Dependencies are JUnit, Hadoop root-directory contract tests, and Router WebHDFS.

Integration points are WebHDFS root listing and Router mount-table behavior. Risks include coverage gaps around root listing, especially because `LISTSTATUS_BATCH` is disabled here. The test signal documents WebHDFS Router root semantics and prevents false failures from generic HDFS root expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractRootDirectory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractSeek.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractSeek.java

This class runs `AbstractContractSeekTest` through Router WebHDFS, but disables three inherited seek edge cases.

Setup and teardown use `RouterWebHDFSContract`; `createContract` returns the WebHDFS contract. `testNegativeSeek`, `testSeekReadClosedFile`, and `testSeekPastEndOfFileThenReseekAndRead` only print "Not supported", indicating WebHDFS or the Router WebHDFS client does not support those generic seek scenarios in this context.

State is the WebHDFS mini cluster and inherited test files. Dependencies include JUnit and Hadoop seek contract tests. Integration points are WebHDFS `OPEN` reads, datanode redirects, and Router path resolution.

Risks include weakened coverage for seek boundary/error behavior and silent passing because disabled tests print instead of asserting a skip assumption. The positive signal is basic seek/read compatibility where inherited supported cases still run through Router WebHDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/TestRouterWebHDFSContractSeek.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/package-info.java

This package-info file documents the purpose of `org.apache.hadoop.fs.contract.router.web`: tests for the WebHDFS contract over the Router.

There are no APIs, classes, functions, state, or persistence behavior beyond the package declaration and Javadoc. Its dependencies are only Java package documentation conventions and the surrounding test package.

Integration is informational: generated Javadoc and IDE/package views can show that this package contains WebHDFS contract tests. Risks are minimal; stale package documentation could mislead maintainers if the package grows beyond WebHDFS contract coverage. Test signal is not applicable beyond compilation of the package declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/web/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestAsyncRpcProtocolPBUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestAsyncRpcProtocolPBUtil.java

This test verifies the asynchronous protobuf RPC utility used by Router protocol translators. It creates a one-handler protobuf RPC server backed by a delayed test implementation, enables client asynchronous mode, and verifies that calls return before server processing completes while `AsyncUtil.syncReturn` later yields the result or exception.

Important methods are `setUp()`, `clear()`, `testAsyncIpcClient()`, and `checkResult()`. Setup configures `AsyncRpcProtocolPBUtil` with `ForkJoinPool.commonPool()`, installs `ProtobufRpcEngine2` for `TestRpcBase.TestRpcService`, starts an RPC server with `TestClientProtocolServerSideTranslatorPB`, creates a proxy, wraps it in `TestClientProtocolTranslatorPB`, and turns on `Client.setAsynchronousMode(true)`. The test calls `add`, `echo`, and `error`; successful calls assert that client call cost is below the server delay and that synced results match; error calls expect a `RemoteException` containing the server-side standby message.

State is per-test RPC server/client state plus global Hadoop IPC asynchronous mode and async responder executor. Dependencies include Hadoop IPC, protobuf test services, `AsyncUtil`, `LambdaTestUtils`, and `Time`.

Risks include global async mode not being restored in this test, common-pool scheduling variability, and timing assertions being sensitive on slow CI machines. The test signal is direct coverage for async RPC result and exception propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestAsyncRpcProtocolPBUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestClientProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestClientProtocol.java

This small interface defines the test protocol used by the async protobuf RPC utility tests. Its methods are `ping()`, `echo(String)`, `error()`, and `add(int, int)`, each declared to throw `IOException`.

There is no implementation, state, or persistence in this file. `TestClientProtocolTranslatorPB` implements the interface on the client side by wrapping protobuf RPC calls in `AsyncRpcProtocolPBUtil.asyncIpcClient`; `TestClientProtocolServerSideTranslatorPB` supplies delayed server behavior through Hadoop's protobuf test service implementation.

Dependencies are only Java `IOException` and the surrounding test classes. Integration is as a simple typed facade over protobuf RPC test calls. Risks are low; any method-signature change must be reflected in the translator and tests. Test signal comes from `TestAsyncRpcProtocolPBUtil`, which exercises all four methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestClientProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestClientProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestClientProtocolServerSideTranslatorPB.java

This server-side test translator extends `TestRpcBase.PBServerImpl` to add deterministic processing delay and error behavior for async RPC tests.

The constructor accepts `processTime` in milliseconds. `error()` sleeps, then throws a `ServiceException` wrapping a `StandbyException("test!")`. `echo()` and `add()` sleep, delegate to the superclass implementation, log request/result/cost, and return protobuf responses. Interrupted sleeps restore the interrupt flag.

State is just the immutable `processTime`. Dependencies include Hadoop IPC protobuf test messages, `RpcController`, `ServiceException`, `StandbyException`, `Time`, and SLF4J logging. Integration is through `TestRpcServiceProtos.TestProtobufRpcProto.newReflectiveBlockingService`, which exposes this implementation to the Hadoop RPC server in `TestAsyncRpcProtocolPBUtil`.

Risks include `res` being null if interruption happens before the superclass response and the finally block logs `res.getMessage()` or `res.getResult()`, which could fail under interruption. The test signal is controlled delayed server behavior that lets async client tests distinguish immediate client return from later server completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestClientProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestClientProtocolTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestClientProtocolTranslatorPB.java

This client-side test translator implements `TestClientProtocol` over `TestRpcBase.TestRpcService`. It is a compact facade for exercising `AsyncRpcProtocolPBUtil.asyncIpcClient`.

`ping()`, `echo(String)`, `error()`, and `add(int,int)` build the corresponding protobuf request messages, call the underlying RPC proxy, and provide response mappers to convert protobuf responses into `Void`, `String`, or `Integer`. `close()` stops the RPC proxy through `RPC.stopProxy`.

State is the final `TestRpcService rpcProxy`. Dependencies include Hadoop IPC RPC, protobuf test message classes, Java `Closeable`, and `AsyncRpcProtocolPBUtil`.

Integration points are the async IPC utility and the delayed server translator. In asynchronous mode, return values are retrieved later through `AsyncUtil.syncReturn`; in synchronous mode the same wrapper still returns mapped values. Risks are mostly test-harness risks: mapper type mismatches would surface at sync-return time, and the translator assumes the proxy implements the protobuf service contract. Test signal comes from `TestAsyncRpcProtocolPBUtil`, which exercises every method and proxy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestClientProtocolTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestRouterClientSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestRouterClientSideTranslatorPB.java

This test validates Router client-side protobuf translators in Hadoop IPC asynchronous mode against a real `MiniDFSCluster` namenode. It does not start a Router; it creates protocol proxies directly to the namenode and exercises Router translator classes.

Setup configures the async responder executor, starts a one-datanode `MiniDFSCluster`, records the namenode address, and creates `RouterClientProtocolTranslatorPB`, `RouterGetUserMappingsProtocolTranslatorPB`, `RouterNamenodeProtocolTranslatorPB`, and `RouterRefreshUserMappingsProtocolTranslatorPB` through `createProxy`. Each test enables `Client.setAsynchronousMode(true)` and restores the previous mode afterward.

`testRouterClientProtocolTranslatorPB()` covers mkdirs, setPermission, getFileInfo, setAcl, setOwner, create, getListing, getDatanodeReport, createSymlink, getFileLinkInfo, rename, delete, and expected `RemoteException` on mkdirs under a deleted parent. Other tests cover user/group mappings, namenode protocol calls (`getTransactionID`, `getBlockKeys`, `rollEditLog`), and refresh-user-mapping calls.

State includes the mini cluster filesystem, global IPC async mode, and translator/proxy instances closed at teardown. Dependencies include HDFS protocol PB classes, `AsyncUtil.syncReturn`, ACL/permission helpers, UGI, and protobuf RPC engine. Risks include global async-mode leakage if teardown fails and broad setup cost. Test signal is high-value coverage that Router PB translators correctly map async return types and exceptions for client, namenode, and user-mapping protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestRouterClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/rbfbalance/TestMountTableProcedure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/rbfbalance/TestMountTableProcedure.java

This class tests `MountTableProcedure`, the RBF balance procedure that rewrites a mount-table entry and toggles mount-point writability during migration.

Global setup starts a `StateStoreDFSCluster` with a Router configured for state store, admin, and RPC. It registers active namenode reports for `ns0` and `ns1`, refreshes caches, and builds `routerConf` pointing at the Router admin address. Each test synchronizes a mock mount table into the state store and resets the Router admin client.

`testUpdateMountpoint()` adds `/test-path`, disables writes, executes a `MountTableProcedure` to move the destination to `ns1:/test-dst`, reloads state-store cache, verifies destination update, reenables writes, and confirms the path now fails with no available namenode rather than read-only. `testDisableAndEnableWrite()` directly verifies read-only enforcement and reenablement. `testSeDeserialize()` writes and reads the procedure through Hadoop `Writable` APIs and checks persisted fields.

State and persistence are the Router state store, mount table records, state-store cache, and procedure serialization bytes. Dependencies include `MountTableManager`, `MountTableStoreImpl`, `DFSClient`, HA state reports, and `LambdaTestUtils.intercept`. Risks include dependence on error-message text and only one Router context. Test signal covers admin RPC integration, cache reload, read-only enforcement, destination mutation, and serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/rbfbalance/TestMountTableProcedure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/rbfbalance/TestRouterDistCpProcedure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/rbfbalance/TestRouterDistCpProcedure.java

This class specializes the shared `TestDistCpProcedure` for Router federation. It verifies that `RouterDistCpProcedure.disableWrite` can mark an RBF mount point read-only during a federation balance flow.

Global setup starts a `StateStoreDFSCluster` with state-store, admin, and RPC services, registers an active `ns0` namenode report, refreshes caches, and records the Router admin address in `routerConf`. The overridden `testDisableWrite()` adds `/test-write -> ns0:/test-write`, reloads the mount-table cache, creates a `DFSClient` to the Router RPC URI, builds a `FedBalanceContext`, executes `RouterDistCpProcedure.disableWrite(context)` at `Stage.FINAL_DISTCP`, and asserts that subsequent `mkdirs` under the mount fails with a read-only mount-point exception.

State is the Router state store, mount-table cache, test mount record, and procedure execution state from the superclass harness. Dependencies include `RouterDistCpProcedure`, `FedBalanceContext`, `DistCpProcedure.Stage`, `MountTableManager`, `DFSClient`, and HA state reports.

Risks include reliance on exact RemoteException text, testing only disable-write behavior rather than full DistCp copy/commit behavior here, and a single-router setup. The test signal is integration coverage between federation-balance DistCp procedure logic and Router mount-table read-only enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/rbfbalance/TestRouterDistCpProcedure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/FederationTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/FederationTestUtils.java

`FederationTestUtils` is a static utility collection for RBF tests. It creates synthetic federation records, waits for Router/namenode state-store visibility, performs common filesystem operations, mutates test clusters, and injects failures with Mockito/Whitebox.

Important APIs include `verifyException`, `createNamenodeReport`, overloaded `waitNamenodeRegistered`, `waitRouterRegistered`, file helpers (`addDirectory`, `createFile`, `readFile`, `deleteFile`, `countContents`, `checkForFileInDirectory`), JMX helper `getBean`, cluster transition helpers (`transitionClusterNSToStandby`, `transitionClusterNSToActive`), Router/FS client factories (`getFileSystem`, `getAdminClient`), `createMountTableEntry`, `refreshRoutersCaches`, `simulateSlowNamenode`, and `simulateThrowExceptionRouterRpcServer`.

Control flow is mostly synchronous helper logic. Wait methods poll with `GenericTestUtils.waitFor`; mount-table creation uses `RouterClient` admin APIs, writes `MountTable` records, refreshes Router caches, then reads entries back. Failure simulation wraps HA contexts or connection managers with spies and replaces private state via Whitebox.

State and persistence touched by this utility include HDFS files, mount-table state-store records, Router and membership caches, JMX MBeans, and mocked internal fields. Dependencies span HDFS, Router admin/state-store APIs, JMX, Mockito, and Hadoop test utilities.

Risks include reflection/Whitebox fragility, exact state polling timeouts, equality checks such as `getNamenodeId() == nnId || equals(nnId)` relying on a null-safe short-circuit, and broad helper scope making tests tightly coupled to internals. Test signal is indirect but extensive: many Router federation tests use these helpers for cluster setup, mount entries, failover state, and fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/FederationTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/MiniRouterDFSCluster.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/MiniRouterDFSCluster.java

`MiniRouterDFSCluster` is the core RBF test fixture that builds an in-process federated HDFS deployment with multiple nameservices, optional HA namenodes, datanodes, and one Router per namenode context. It supplies client/admin handles and lifecycle helpers used throughout Router tests.

Important types are `RouterContext` and `NamenodeContext`. `RouterContext` owns a `Router`, configuration, bound RPC/HTTP ports, `FileContext`, DFS client, admin client, and helper methods for Router-backed `FileSystem` and proxy-provider variants. `NamenodeContext` owns namenode identity, bound addresses, `FileContext`, DFS client, and configuration suffix logic.

Important cluster APIs include constructors for HA/non-HA shapes, `addRouterOverrides`, `addNamenodeOverrides`, `generateNamenodeConfiguration`, `generateClientConfiguration`, `generateRouterConfiguration`, `configureNameservices`, datanode/storage/rack setters, context lookup methods, `startCluster`, `startRouters`, `registerNamenodes`, `waitNamenodeRegistration`, `waitActiveNamespaces`, HA transition helpers, `shutdown`, `stopRouter`, fixture path helpers, `createTestDirectoriesNamenode`, `deleteAllFiles`, `installMockLocations`, and `waitClusterUp`.

State and persistence include in-memory lists of nameservices/namenode/router contexts, a `MiniDFSCluster`, generated `Configuration` objects, static random selection, mount mappings in `MockResolver`, Router/namenode state, and HDFS namespace contents. Configuration generation binds random ports, mock resolver classes, Router heartbeat/cache intervals, monitor-namenode lists, default nameservice, and safemode disabled for tests.

Dependencies include `MiniDFSCluster`, `MiniDFSNNTopology`, Router services, resolver interfaces, HA transition APIs, `MockResolver`, HDFS clients, and federation test utilities. Risks include broad mutable static-like fixture state, random router/namenode selection causing nondeterministic coverage, caught startup exceptions that log but do not always rethrow, and test assumptions tied to mock resolvers rather than real state-store-backed mount tables. Test signal is foundational: this fixture underpins contract tests and many federation integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/MiniRouterDFSCluster.java -->
