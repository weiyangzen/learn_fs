# Research Group: subset-b-007412

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto2-generated/org/apache/hadoop/ipc/protobuf/TestRpcServiceProtosLegacy.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto2-generated/org/apache/hadoop/ipc/protobuf/TestRpcServiceProtosLegacy.java

## Purpose
`TestRpcServiceProtosLegacy.java` is generated protobuf Java code for `test_rpc_service_legacy.proto`. It supplies Hadoop IPC tests with legacy proto2 `com.google.protobuf.Service`, asynchronous stubs, blocking stubs, reflective services, method dispatch, request/response prototypes, and file descriptors for several test RPC services. The file is test-only generated infrastructure and intentionally mirrors the protobuf compiler output rather than hand-written Hadoop style.

## Important APIs, Types, And Functions
The outer `TestRpcServiceProtosLegacy` class is a non-instantiable namespace with `registerAllExtensions(ExtensionRegistry)` and `getDescriptor()`.

Seven generated service wrappers are present:
- `TestProtobufRpcProto`: the main service with 18 RPCs: `ping`, `echo`, `error`, `error2`, `slowPing`, `echo2`, `add`, `add2`, `testServerGet`, `exchange`, `sleep`, `lockAndSleep`, `getAuthMethod`, `getAuthUser`, `echoPostponed`, `sendPostponed`, `getCurrentUser`, and `getServerRemoteUser`.
- `TestProtobufRpc2Proto`: smaller service with `ping2`, `echo2`, and `sleep`.
- `OldProtobufRpcProto`: compatibility service with `ping` and `echo`, both using empty request/response messages.
- `NewProtobufRpcProto`: compatibility-evolution service with `ping` and an `echo` that uses `OptRequestProto`/`OptResponseProto`.
- `NewerProtobufRpcProto`: another two-method compatibility service using empty request/response messages.
- `CustomProto`: single-method `ping` service.
- `TestProtobufRpcHandoffProto`: single-method `sleep` service using `SleepRequestProto2` and `SleepResponseProto2`.

Each service exposes an asynchronous `Interface`, `newReflectiveService(Interface)`, `newStub(RpcChannel)`, a `BlockingInterface`, `newReflectiveBlockingService(BlockingInterface)`, and `newBlockingStub(BlockingRpcChannel)`. Message types come from `TestProtosLegacy`, and dispatch uses protobuf runtime types such as `RpcController`, `RpcCallback`, `RpcChannel`, `BlockingRpcChannel`, `Descriptors.MethodDescriptor`, and `ServiceException`.

## Control Flow
Asynchronous calls flow through `callMethod(MethodDescriptor, RpcController, Message, RpcCallback<Message>)`. The method descriptor is first checked against the service descriptor, then `method.getIndex()` drives a switch that casts the generic `Message` to the generated request type and specializes the callback to the generated response type.

Blocking calls follow the same descriptor validation and method-index switch in `callBlockingMethod`, returning the concrete response `Message` from the provided `BlockingInterface`. Client stubs invert that flow: each generated method calls `channel.callMethod(...)` or `channel.callBlockingMethod(...)` with `getDescriptor().getMethods().get(index)`, the concrete request, the response default instance, and generalized callback plumbing.

The static initializer builds the file descriptor from serialized descriptor data and declares `TestProtosLegacy.getDescriptor()` as its dependency. Service descriptors are selected by ordinal from `getDescriptor().getServices().get(0..6)`, so the generated service order is part of the runtime contract.

## State And Persistence
The file has no durable application state. It has static protobuf descriptor state initialized once per classloader. Stub instances retain only an RPC channel reference. Request and response prototypes are immutable protobuf default instances.

## Dependencies And Integration Points
This class integrates Hadoop IPC tests with the legacy protobuf service API. It depends on `TestProtosLegacy` message classes, protobuf runtime service descriptors, and Hadoop test RPC implementations that implement the generated interfaces. The generated descriptor name, method ordinals, and request/response classes must stay synchronized with `test_rpc_service_legacy.proto` and `test_legacy.proto`.

## Risks
Because this is generated code, manual edits are brittle and likely to be overwritten. The largest behavioral risk is descriptor ordinal drift: adding, removing, or reordering proto services or methods changes method indexes and could break reflective dispatch or stubs compiled against old expectations. Wrong method descriptors intentionally throw `IllegalArgumentException`; wrong request message types fail via casts. The legacy `com.google.protobuf.Service` API is older than modern protobuf lite/gRPC patterns, so tests depend on keeping the generated proto2 runtime available.

## Test Signals
The file itself is test infrastructure. Useful signals are compilation of generated sources, Hadoop IPC protobuf tests that instantiate reflective services and stubs, compatibility tests around old/new service descriptors, and tests that exercise delayed responses, authentication user methods, errors, blocking calls, and handoff sleep behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto2-generated/org/apache/hadoop/ipc/protobuf/TestRpcServiceProtosLegacy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/ftp.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/ftp.xml

## Purpose
`ftp.xml` is a Hadoop filesystem contract-test configuration for FTP-backed filesystems, especially remote Unix FTP targets. It declares which filesystem behaviors the generic contract test suite should expect or skip.

## Important Properties
The fixture disables root tests with `fs.contract.test.root-tests-enabled=false`, marks FTP as case-sensitive, and declares no append, no block locality, no concat, no seek support, no Unix permission support, strict exceptions enabled, and seek-past-EOF rejected. It marks atomic directory delete and atomic rename as supported.

## Control Flow
There is no executable control flow. Hadoop `Configuration` and contract test code load the XML and branch test expectations from the `fs.contract.*` keys. A false capability suppresses or alters tests that would otherwise assume HDFS-like semantics.

## State And Persistence
The file is a static test resource. It persists only declarative capability values and does not create runtime state. Its values can influence tests that reach an external FTP server configured elsewhere.

## Dependencies And Integration Points
It integrates with Hadoop's filesystem contract test framework and FTP filesystem implementation. Credentials and host-specific settings come from other configuration, notably the test `core-site.xml` entries for localhost FTP user/password.

## Risks
The risk is capability drift: if FTP behavior changes but this fixture is not updated, the contract suite may either hide real regressions or assert invalid semantics. Enabling root tests or seek incorrectly could make tests destructive or flaky against external servers.

## Test Signals
Contract test outcomes for FTP are the main signal. Failures around rename atomicity, EOF seeking, strict exception type expectations, and permissions indicate mismatch between fixture claims and actual FTP filesystem behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/ftp.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/localfs.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/localfs.xml

## Purpose
`localfs.xml` defines filesystem contract expectations for Hadoop's checksummed local filesystem. It captures semantics that differ from raw local disk, especially checksum handling and append behavior.

## Important Properties
The file declares case sensitivity and Unix permissions as true, disables root tests, sets `fs.contract.test.random-seek-count=1000`, and enables rename-created destination directories, rename overwrite, and empty-destination-directory removal. It marks append unsupported because checksummed filesystems do not support append, while atomic directory delete, atomic rename, seek, seek on closed file, settimes, getfilestatus, and vector early EOF check are supported. Block locality, concat, and strict exceptions are false, and seek past EOF is rejected. `supports-settimes` and `supports-getfilestatus` appear twice with the same true value.

## Control Flow
Contract tests consume these values through `Configuration` and choose which generic tests to run or which behavior to assert. The duplicate properties rely on Hadoop configuration's normal repeated-key handling; because the values agree, the duplication is harmless but noisy.

## State And Persistence
The file is a static test resource and creates no state. It points tests at local filesystem semantics that may still vary by OS for case sensitivity and permission enforcement, despite comments noting runtime OS determination.

## Dependencies And Integration Points
It integrates with local filesystem contract tests and Hadoop's `LocalFileSystem` behavior. It is related to `rawlocal.xml`, but differs on append and EOF-seek expectations due to checksum wrappers.

## Risks
The main risk is platform-dependent behavior. Case sensitivity and Unix permissions can be different on Windows or mounted filesystems, so hard-coded true values can be brittle if runtime overrides do not adjust them. Duplicate properties can obscure future edits if only one copy is changed.

## Test Signals
Signals include generic contract failures for append, rename, seek past EOF, timestamp setting, and vector IO early EOF handling. Failures that appear only on specific OSes usually indicate fixture/platform mismatch rather than core API breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/localfs.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/rawlocal.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/rawlocal.xml

## Purpose
`rawlocal.xml` defines contract-test capabilities for Hadoop's raw local filesystem, where operations map more directly to local disk without the checksum wrapper.

## Important Properties
It marks case sensitivity, Unix permissions, append, atomic directory delete, atomic rename, rename-created destination directories, rename overwrite, empty-directory destination removal, seek, seek on closed file, settimes, getfilestatus, content check, hflush, hsync, metadata update on hsync, and vector overlapping ranges as supported. It disables root tests, sets random seek count to 1000, marks block locality and concat unsupported, sets strict exceptions false, and says seek past EOF is not rejected.

## Control Flow
There is no local execution logic. Contract test classes load the file and use `fs.contract.*` booleans to decide which assertions are meaningful for raw local filesystem implementations.

## State And Persistence
The XML is persistent test metadata only. Runtime state is in temporary local files created by the contract tests, not in this resource.

## Dependencies And Integration Points
It integrates with tests for `RawLocalFileSystem` and generic filesystem contracts. The hflush/hsync flags connect it to output stream sync semantics and metadata-update assertions that are not expected of all filesystems.

## Risks
Raw local semantics are highly OS- and filesystem-dependent. Permissions, case sensitivity, hsync metadata behavior, and seek-past-EOF behavior can differ across platforms or mounts. Overstated capabilities can make contract tests flaky outside Linux-like environments.

## Test Signals
Important signals are contract tests for append, hflush/hsync, metadata durability, rename behavior, EOF seeking, content validation, and vector IO range handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/rawlocal.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/sftp.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/sftp.xml

## Purpose
`sftp.xml` is the filesystem contract-test profile for SFTP-backed filesystems. It is similar to the FTP contract but differs on seek support.

## Important Properties
The fixture disables root tests, declares case sensitivity true, append false, atomic directory delete true, atomic rename true, block locality false, concat false, seek true, seek-past-EOF rejected true, strict exceptions true, and Unix permissions false.

## Control Flow
The file is read by the contract test harness. Tests use the capability flags to include or exclude generic filesystem behavior checks for SFTP.

## State And Persistence
It stores only static XML properties. Test state is external: temporary paths on the SFTP server and any credentials/server details configured elsewhere.

## Dependencies And Integration Points
It integrates with Hadoop's SFTP filesystem implementation and generic contract tests. It depends on an accessible SFTP environment when those tests are enabled.

## Risks
SFTP servers can vary in rename atomicity, permission reporting, and seek implementation. If the configured server does not match this profile, tests may fail for environmental reasons. Root tests remain disabled to avoid destructive assumptions.

## Test Signals
Contract tests around seek, EOF rejection, atomic rename/delete, and strict exceptions are the primary signals that this fixture still matches the target SFTP implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/contract/sftp.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/core-site.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/core-site.xml

## Purpose
This test `core-site.xml` provides baseline Hadoop common configuration for unit and integration tests. It supplies temporary-directory defaults, FTP localhost credentials, simple authentication, and fixed NFS test ports.

## Important Properties
The file sets `hadoop.tmp.dir=build/test`, `fs.ftp.user.localhost=user`, `fs.ftp.password.localhost=password`, `hadoop.security.authentication=simple`, `nfs3.server.port=2079`, and `nfs3.mountd.port=4272`.

## Control Flow
There is no executable logic. Hadoop test code loads it through `Configuration`, and downstream components branch on authentication mode, temporary path, FTP credential lookup, or NFS port allocation.

## State And Persistence
The XML itself is static. It causes runtime state under `build/test` and may bind local ports 2079 and 4272 in NFS-related tests.

## Dependencies And Integration Points
It integrates with Hadoop Common tests, FTP filesystem tests, and NFS gateway tests. The FTP credentials line up with localhost-specific FTP contract tests and avoid prompting or relying on production credential stores.

## Risks
Hard-coded ports can collide with local services or parallel test runs. The placeholder FTP password is test-only but should not leak into production config. Changing `hadoop.security.authentication` from `simple` would alter many test assumptions.

## Test Signals
Signals include configuration-loading tests, FTP contract tests that resolve localhost credentials, NFS tests that bind the configured ports, and security tests expecting simple auth unless they override it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/core-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/fi-site.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/fi-site.xml

## Purpose
`fi-site.xml` is a fault-injection test configuration. It sets a wildcard probability for fault injection controls used by Hadoop tests.

## Important Properties
The single property `fi.*=0.00` effectively disables all wildcard fault-injection events unless a test overrides a narrower key.

## Control Flow
Fault-injection-aware test code reads matching `fi.*` keys from `Configuration` and decides whether to trigger injected failures. With `0.00`, default control flow remains non-faulting.

## State And Persistence
The file persists only the default injection probability. It creates no state and does not record injection events.

## Dependencies And Integration Points
It integrates with Hadoop's fault-injection utilities and tests that intentionally override or consume `fi.*` properties.

## Risks
If the default is raised, unrelated tests can become nondeterministic. If the file is not loaded where expected, tests that rely on a known no-fault baseline can become environment-dependent.

## Test Signals
Fault-injection tests should show deterministic non-injected behavior by default, with explicit overrides enabling failure paths in targeted tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/fi-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/hadoop-policy.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/hadoop-policy.xml

## Purpose
This test `hadoop-policy.xml` defines service authorization ACLs for Hadoop protocol tests. It is a permissive policy fixture for most services, with a self-user restriction for authorization refresh.

## Important Properties
The file sets `*` ACLs for `security.client.protocol.acl`, `security.client.datanode.protocol.acl`, `security.datanode.protocol.acl`, `security.inter.datanode.protocol.acl`, `security.namenode.protocol.acl`, `security.inter.tracker.protocol.acl`, `security.job.submission.protocol.acl`, and `security.task.umbilical.protocol.acl`. `security.refresh.policy.protocol.acl` is set to `${user.name}`.

## Control Flow
There is no code, but Hadoop service-authorization code loads the policy and checks callers against the configured ACLs before allowing protocol access. The refresh policy entry exercises variable substitution and narrower authorization.

## State And Persistence
The file is static policy metadata. Runtime authorization state is held by Hadoop security managers and service authorization refresh code after loading this XML.

## Dependencies And Integration Points
It integrates with Hadoop RPC service authorization tests, NameNode/DataNode protocol ACL tests, MapReduce legacy protocol tests, and refresh-policy tests.

## Risks
The broad `*` ACLs are test conveniences and unsafe for production. If service property names drift from protocol implementations, tests may accidentally use defaults. Variable substitution in `${user.name}` must remain available for refresh policy tests.

## Test Signals
Signals include service-authorization acceptance for broad protocols, denial/allowance behavior for refresh-policy callers, and successful reload of authorization policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/hadoop-policy.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/krb5.conf -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/krb5.conf

## Purpose
`krb5.conf` is a Kerberos configuration template for Hadoop security tests, especially MiniKDC-style local realms.

## Important Entries
The file includes placeholder comments for `_KDC_TCP_PORT_` and `_KDC_UDP_PORT_`. It defines realm `APACHE.ORG` with `kdc = localhost:_KDC_PORT_`, and maps `.apache.org` and `apache.org` to `APACHE.ORG` in `[domain_realm]`.

## Control Flow
No code runs in this file. Test setup usually replaces `_KDC_PORT_` with the dynamically allocated MiniKDC port before launching Kerberos-authenticated tests.

## State And Persistence
The file is a static template. Runtime Kerberos tickets, keytabs, and KDC state are created by tests outside this file.

## Dependencies And Integration Points
It integrates with JVM Kerberos/GSS configuration, Hadoop security authentication tests, and local MiniKDC instances.

## Risks
If placeholders are not replaced, Kerberos tests fail to locate the KDC. Hard-coded realm/domain mappings are test-specific and should not be reused for production. Port mismatches can cause confusing authentication failures.

## Test Signals
Successful Kerberos login, service principal resolution, and Hadoop secure RPC tests indicate the template was rendered and loaded correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/krb5.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/org/apache/hadoop/security/secure-hdfs-site.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/org/apache/hadoop/security/secure-hdfs-site.xml

## Purpose
`secure-hdfs-site.xml` is a minimal HDFS security test configuration resource. It enables data transfer protection through a SASL properties resolver.

## Important Properties
The single property is `dfs.data.transfer.protection=org.apache.hadoop.security.SaslPropertiesResolver`.

## Control Flow
HDFS/security tests load the resource into `Configuration`; data-transfer setup code reads the property and configures SASL negotiation/protection behavior accordingly.

## State And Persistence
The file has no runtime state. It influences in-memory HDFS security configuration for tests.

## Dependencies And Integration Points
It integrates with Hadoop security tests under `org/apache/hadoop/security`, HDFS data transfer protection code, and `SaslPropertiesResolver`.

## Risks
The configured value is a class name in a property whose usual values may be expected to be protection levels in other contexts. Tests relying on this fixture are sensitive to how `dfs.data.transfer.protection` is parsed. Missing the resource from the test classpath disables the intended secure path.

## Test Signals
Secure HDFS transfer tests and SASL resolver tests should show that protected data transfer setup is used when this resource is loaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/org/apache/hadoop/security/secure-hdfs-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/test-fake-default.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/test-fake-default.xml

## Purpose
`test-fake-default.xml` is a fake Hadoop default configuration file used by unit tests around configuration defaults and deprecated-key handling.

## Important Properties
It defines `tests.fake-default.new-key=tests.fake-default.value` with a description saying it is the default value for the "new" key of a deprecated pair.

## Control Flow
Configuration tests load this resource as if it were a `*-default.xml` file and verify default lookup/deprecation behavior.

## State And Persistence
The XML is static test metadata. It contributes an in-memory default configuration entry during tests.

## Dependencies And Integration Points
It integrates with Hadoop `Configuration` tests, particularly tests of deprecation maps and default resource loading.

## Risks
Because this is a fake default resource, using it outside tests can pollute configuration namespaces. Renaming the key without updating deprecation tests would break expected old/new key mapping.

## Test Signals
Tests should verify that the new key resolves to `tests.fake-default.value` and that deprecated aliases map to the same effective value where configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/test-fake-default.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/testConf.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/testConf.xml

## Purpose
`testConf.xml` is a command-output specification for Hadoop `fs` shell help tests. It describes commands to run and comparators for expected help text.

## Important Structure
The top-level mode is `test`, with comments indicating `nocompare` can run commands and dump output. Each `<test>` contains a description, `<test-commands>`, optional cleanup commands, and comparators. Comparator types include `SubstringComparator`, `RegexpComparator`, `TokenComparator`, and `RegexpAcrossOutputComparator`.

The covered commands are mostly `hadoop fs -help` variants: general `-help`, `ls`, deprecated `lsr`, `du`, deprecated `dus`, `count`, `mv`, `cp`, `rm`, `rmdir`, deprecated `rmr`, `put`, `copyFromLocal`, `moveFromLocal`, `get`, `getmerge`, `cat`, `checksum`, `copyToLocal`, `moveToLocal`, `mkdir`, `setrep`, `touch`, `touchz`, `test`, `stat`, `tail`, `chmod`, `chown`, `chgrp`, `find`, and `help`.

## Control Flow
The XML is interpreted by Hadoop's command test harness. For each test, the harness invokes the listed `hadoop fs` command, captures output, and applies the configured comparators in order. Most tests assert regex fragments of help output; `find` uses a cross-output comparator for a larger multi-line help block.

## State And Persistence
The file is static expected-output data. Most tests are read-only help commands and have empty cleanup. Runtime state is limited to captured command output and test framework reports.

## Dependencies And Integration Points
It integrates with FsShell help text, command-line parser behavior, and the comparator framework. It also encodes compatibility expectations for deprecated aliases such as `lsr`, `dus`, and `rmr`.

## Risks
Help text changes can break tests even when command behavior is unchanged. Several comparators are sensitive to whitespace and regex escaping. There is a malformed-looking nested comparator under the `put` test, which may be accepted by the historical harness but is structurally fragile. Long multi-line expectations for `find` can become stale when help text evolves.

## Test Signals
Passing command tests show that user-facing help syntax, option lists, deprecated command messages, and selected descriptions remain stable. Failures should be triaged as either intentional documentation/help updates requiring fixture changes or regressions in command registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/testConf.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/xml/entity-dtd.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/xml/entity-dtd.xml

## Purpose
`entity-dtd.xml` is an XML parser test fixture with an inline DTD and entity declaration.

## Important Structure
It declares an internal DTD for `lolz`, defines entity `lol` as text, and uses `&lol;` in the document body.

## Control Flow
XML parser tests load the file to exercise inline DTD/entity handling. The expected parse result depends on whether entity expansion is allowed in that test path.

## State And Persistence
The file is static XML data and creates no state.

## Dependencies And Integration Points
It integrates with Hadoop XML parsing and configuration/security hardening tests, especially tests around DTD and entity processing.

## Risks
Entity expansion is security-sensitive. This small fixture is benign, but parser configuration must avoid general XXE-style exposure when external entities are involved.

## Test Signals
Parser tests should either expand the internal entity as expected or reject DTD/entity processing in hardened modes with the intended exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/xml/entity-dtd.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/xml/external-dtd.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/xml/external-dtd.xml

## Purpose
`external-dtd.xml` is an XML parser security fixture that references an external DTD named `address.dtd`.

## Important Structure
The document declares `<!DOCTYPE address SYSTEM "address.dtd">` and contains a simple `address` element with `name`, `company`, and `phone` children.

## Control Flow
Parser tests load this file to verify how external DTD resolution is handled. Hardened parser configurations should prevent unintended external resource access where appropriate.

## State And Persistence
It is static XML data only. Any external resolution behavior is performed by the parser/test harness at runtime.

## Dependencies And Integration Points
It integrates with XML parser tests and security hardening around external entities and DTD loading.

## Risks
External DTD processing can lead to XXE or filesystem/network access if parser settings are unsafe. This fixture is useful precisely because it can expose accidental external resolution.

## Test Signals
Expected signals are either a controlled rejection of external DTD resolution or successful parsing only when a test explicitly permits and supplies the external DTD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/xml/external-dtd.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/scripts/hadoop-functions_test_helper.bash -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/scripts/hadoop-functions_test_helper.bash

## Purpose
This Bash helper provides common setup, teardown, and string-check utilities for Bats tests of Hadoop shell functions.

## Important Functions
`setup()` clears `LD_LIBRARY_PATH`, creates a unique temporary directory under `target/test-dir`, exports `TMP`, resolves `TESTBINDIR`, points `HADOOP_LIBEXEC_DIR` at `src/main/bin`, enables `HADOOP_SHELL_SCRIPT_DEBUG`, unsets `HADOOP_CONF_DIR`, `HADOOP_HOME`, and `HADOOP_PREFIX`, sets `QATESTMODE=true`, sources `hadoop-functions.sh`, and pushes into the temp directory. `teardown()` pops the directory and removes `TMP`. `strstr()` prints `true` if a substring occurs in a string and `false` otherwise.

## Control Flow
Bats automatically calls `setup` and `teardown` around each test. The helper normalizes the shell environment before sourcing production shell functions, then isolates test filesystem effects in a per-process temp directory.

## State And Persistence
Temporary state is created under `../../../target/test-dir/bats.$$.${RANDOM}` and removed in teardown. Environment variables are deliberately changed for the test process.

## Dependencies And Integration Points
It depends on Bats conventions, `BATS_TEST_DIRNAME`, `hadoop-functions.sh`, and the Hadoop source tree layout. It is consumed by shell tests in the same test scripts directory.

## Risks
Unquoted `mkdir -p ${RELTMP}` is safe for generated paths but remains shell-sensitive. If teardown is skipped after a hard kill, temp directories can remain. Source tree layout changes can break `HADOOP_LIBEXEC_DIR` resolution.

## Test Signals
Bats tests that source this helper should run in isolated temp directories and load production shell functions. Failures during setup usually indicate missing `BATS_TEST_DIRNAME`, broken path assumptions, or syntax errors in `hadoop-functions.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/scripts/hadoop-functions_test_helper.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/scripts/process_with_sigterm_trap.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/scripts/process_with_sigterm_trap.sh

## Purpose
This Bash script is a test process that records its PID and remains alive while trapping termination signals. It supports tests of process management and signal handling.

## Important Behavior
It installs traps that print messages for `SIGTERM` and `SIGINT`, writes its PID to the first positional argument, then loops forever sleeping 1.3 seconds at a time.

## Control Flow
Startup registers traps, emits `$$` to the supplied file path, and enters an infinite loop. Signals do not terminate the process by default because the trap handlers only echo messages; external tests must use stronger termination or cleanup logic if they need it to exit.

## State And Persistence
The script writes a PID file at `$1`. It otherwise maintains only process state and stdout output from traps.

## Dependencies And Integration Points
It integrates with Hadoop shell/process tests that need a long-lived child process and deterministic signal observability.

## Risks
If called without an argument, PID-file writing fails. Because trapped `SIGTERM` does not exit, tests must avoid leaving the process running. The infinite loop can leak processes if cleanup fails.

## Test Signals
Expected signals are the PID file content and observable `SIGTERM trapped!` or `SIGINT  trapped!` output when tests send signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/scripts/process_with_sigterm_trap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/scripts/run-bats.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/scripts/run-bats.sh

## Purpose
`run-bats.sh` is the wrapper that runs Hadoop Common shell tests written in Bats and writes TAP output for Maven/test reporting.

## Important Behavior
It creates `../../../target/surefire-reports` and `../../../target/tap`, locates `bats` with `which`, writes a skip-style TAP file and exits 0 if Bats is unavailable, then runs every `*.bats` file with `bats -t`, teeing output to `target/tap/<test>.tap`. It accumulates pipeline exit status via `PIPESTATUS[0]` and exits 1 if any Bats file fails.

## Control Flow
The script is linear: prepare directories, detect tool availability, iterate Bats files, aggregate exit code, and return success/failure. Missing Bats is treated as a skipped test environment rather than a build failure.

## State And Persistence
It writes TAP files under `target/tap` and ensures surefire report directories exist. It does not clean prior TAP files.

## Dependencies And Integration Points
It depends on Bash, Bats, and the shell test layout. It integrates with Maven Surefire or build scripts that inspect TAP/surefire outputs.

## Risks
If no `*.bats` files match and shell globbing remains default, the loop may attempt to run a literal `*.bats`. `exitcode` is not initialized explicitly; Bash arithmetic treats empty as zero, but this is implicit. Missing Bats exits 0, which can hide unexecuted shell tests in CI unless the skip output is monitored.

## Test Signals
Successful runs create TAP files for each Bats test and return 0. Failure of any Bats test returns 1. Missing Bats creates `shelltest.tap` with a "not ok - no bats executable found" message but exits 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/scripts/run-bats.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/dev-support/findbugsExcludeFile.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/dev-support/findbugsExcludeFile.xml

## Purpose
This SpotBugs/FindBugs filter suppresses known or intentional warnings in the Hadoop KMS module.

## Important Matches
It suppresses `NP_NULL_PARAM_DEREF` for `KMSAudit.op`, `NP_ALWAYS_NULL` for `KMSWebApp`, `ST_WRITE_TO_STATIC_FROM_INSTANCE_METHOD` for `KMSWebApp`, `DM_EXIT` for `KMSWebApp`, and `REC_CATCH_EXCEPTION` for `KMS`.

## Control Flow
SpotBugs reads this XML during the Maven build and filters matching bug reports from the KMS analysis result. There is no runtime effect on KMS code.

## State And Persistence
The file persists static suppression rules only. It does not store analysis output.

## Dependencies And Integration Points
It is referenced by the KMS `pom.xml` in the `spotbugs-maven-plugin` configuration together with the repository-wide global exclusion file.

## Risks
Suppressions can hide real regressions if matching code changes semantics while preserving class and bug pattern names. The `DM_EXIT` suppression documents intentional servlet-container termination on initialization failure, which remains operationally sensitive.

## Test Signals
The main signal is SpotBugs passing for the KMS module without reintroducing these known warnings. New warnings outside this filter should still fail or be reported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/pom.xml

## Purpose
The KMS `pom.xml` defines the Maven module for Apache Hadoop KMS. It declares module identity, dependencies, test behavior, site generation, test-jar creation, SpotBugs filtering, and distribution assembly.

## Important Build Metadata
The module inherits from `hadoop-project` version `3.6.0-SNAPSHOT`, has artifactId `hadoop-kms`, packaging `jar`, and name/description `Apache Hadoop KMS`.

Compile/runtime dependencies include Hadoop auth/common, shaded Guava, Jersey components, Jakarta Servlet API, Jetty server/webapp/util, JAXB runtime, reload4j, SLF4J APIs/bindings, JUL bridge, Dropwizard metrics, and Jackson databind. Test dependencies include `hadoop-minikdc`, `mockito-inline`, Hadoop Common test-jar, Curator test, and Bouncy Castle provider.

## Control Flow
Maven lifecycle configuration drives behavior:
- Surefire runs with one fork, no fork reuse, one thread, 600-second fork timeout, and `TimedOutTestsListener`.
- AntRun transforms `src/main/resources/kms-default.xml` to site HTML during the `site` phase.
- Jar plugin attaches a test-jar in `prepare-package`.
- SpotBugs uses module and global exclusion filters.
- The `dist` profile assembles the `hadoop-kms-dist` descriptor during `package`.

## State And Persistence
The POM has no runtime state. It creates build artifacts under Maven `target`, including jars, test-jar, site HTML, and optional distribution assembly.

## Dependencies And Integration Points
The module integrates KMS server code with Hadoop Common/Auth, servlet/Jersey/Jetty web layers, metrics/logging, Kerberos test support, and Hadoop assembly packaging. Exclusions on `hadoop-common` prevent conflicting old servlet/JSP/Jetty/stax dependencies from entering this webapp module.

## Risks
Dependency drift is the main risk: servlet/Jetty/Jersey versions must stay compatible with the rest of Hadoop. Single-threaded, non-reused fork tests reduce interference but can increase build time. The SpotBugs filter can mask issues if over-broad. The distribution profile relies on `hadoop-assemblies` matching the module version.

## Test Signals
Signals include `mvn test` for KMS with timeout listener behavior, successful creation of the KMS test-jar, successful SpotBugs analysis with intended excludes, generated site config docs, and package success under the `dist` profile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/conf/kms-acls.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/conf/kms-acls.xml

## Purpose
`kms-acls.xml` is the default KMS ACL configuration file. Comments state it is hot-reloaded when it changes.

## Important Properties
Global KMS operation ACLs are all set to `*`: `hadoop.kms.acl.CREATE`, `DELETE`, `ROLLOVER`, `GET`, `GET_KEYS`, `GET_METADATA`, `SET_KEY_MATERIAL`, `GENERATE_EEK`, and `DECRYPT_EEK`. Default per-key ACLs are also `*` for `default.key.acl.MANAGEMENT`, `GENERATE_EEK`, `DECRYPT_EEK`, and `READ`.

## Control Flow
KMS authorization code loads this XML and checks user identities/groups against global operation ACLs and key-specific/default key ACLs. Hot reload means changes can alter authorization behavior in a running KMS process.

## State And Persistence
The file persists ACL policy. Runtime KMS maintains an in-memory parsed view and refreshes it when the file changes.

## Dependencies And Integration Points
It integrates with KMS REST/API authorization, key management operations, crypto extension operations, and ACL reload handling.

## Risks
The shipped defaults are fully permissive and must be tightened for secure deployments. Hot reload is useful but also means accidental edits can immediately broaden access. CREATE and ROLLOVER descriptions note that GET ACL membership controls whether key material is returned, so ACL combinations matter.

## Test Signals
KMS ACL tests should verify default allow behavior, operation-specific checks, key ACL fallback, and hot-reload behavior after file changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/conf/kms-acls.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/conf/kms-env.sh -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/conf/kms-env.sh

## Purpose
`kms-env.sh` is the KMS-specific environment override file sourced after `hadoop-env.sh`.

## Important Variables
It documents commented exports for `KMS_CONFIG`, `KMS_LOG`, `KMS_TEMP`, `KMS_HTTP_PORT`, `KMS_MAX_THREADS`, `KMS_MAX_HTTP_HEADER_SIZE`, `KMS_SSL_ENABLED`, `KMS_SSL_KEYSTORE_FILE`, and `KMS_SSL_KEYSTORE_PASS`.

## Control Flow
KMS launch scripts source this file and use any uncommented exports to configure paths, HTTP server limits, and SSL settings. As checked in, it performs no assignments because all examples are comments.

## State And Persistence
The file persists administrator-configured environment overrides. Runtime state is shell environment visible to KMS startup scripts and the JVM they launch.

## Dependencies And Integration Points
It integrates with Hadoop daemon startup scripts and the KMS web server bootstrap. Variables refer to common Hadoop env values such as `HADOOP_CONF_DIR`, `HADOOP_LOG_DIR`, and `HADOOP_HOME`.

## Risks
Plaintext `KMS_SSL_KEYSTORE_PASS` in an environment file is operationally sensitive if uncommented. Misconfigured temp/log/config paths can prevent startup or split logs. Raising thread/header limits can affect resource use.

## Test Signals
Startup-script tests or integration runs should confirm overrides are picked up when exported and defaults apply when the file remains commented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/conf/kms-env.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/conf/kms-site.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/conf/kms-site.xml

## Purpose
`kms-site.xml` is the site-specific KMS configuration placeholder shipped with the module.

## Important Structure
The file contains an empty `<configuration>` element with the standard license header. No properties are set by default.

## Control Flow
KMS loads this resource as part of its configuration stack. As shipped, it contributes no overrides; administrators or tests can add properties to customize KMS behavior.

## State And Persistence
The file is persistent configuration but empty by default. Runtime KMS state comes from other config defaults and any local edits.

## Dependencies And Integration Points
It integrates with the KMS server configuration loader and deployment packaging. It is the expected local override point corresponding to documented KMS defaults.

## Risks
An empty site file is safe, but deployments that assume secure defaults may miss required provider, authentication, HTTP, or ACL settings. Local edits should be tracked carefully because this file is a central override point.

## Test Signals
Configuration-loading tests should verify that an empty `kms-site.xml` parses successfully and that explicit test overrides can be added without schema issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/conf/kms-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/EagerKeyGeneratorKeyProviderCryptoExtension.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/EagerKeyGeneratorKeyProviderCryptoExtension.java

## Purpose
`EagerKeyGeneratorKeyProviderCryptoExtension` is a private KMS server-side decorator for `KeyProviderCryptoExtension`. It pre-generates encrypted data encryption keys and serves them from a `ValueQueue` cache to reduce latency for `generateEncryptedKey`.

## Important APIs, Types, And Functions
The class extends `KeyProviderCryptoExtension` and exposes cache configuration constants under `hadoop.security.kms.encrypted.key.cache.*`: `size` default 100, `low.watermark` default 0.30, `expiry` default 43,200,000 ms, and `num.fill.threads` default 2.

The nested `CryptoExtension` implements `KeyProviderCryptoExtension.CryptoExtension`. It owns the underlying `KeyProviderCryptoExtension` delegate and a `ValueQueue<EncryptedKeyVersion>`.

`EncryptedQueueRefiller.fillQueueForKey(...)` generates the requested number of encrypted keys by repeatedly calling the delegate's `generateEncryptedKey(keyName)` and adds them to the queue. `warmUpEncryptedKeys(...)` initializes queues, `drain(String)` clears a key queue, `generateEncryptedKey(String)` returns `encKeyVersionQueue.getNext(...)`, and decrypt/reencrypt methods delegate directly.

The outer constructor wraps the supplied provider with the eager `CryptoExtension`. Overrides of `rollNewVersion(String)`, `rollNewVersion(String, byte[])`, and `invalidateCache(String)` call the superclass then drain the affected key cache.

## Control Flow
On construction, the cache reads size, low-watermark, expiry, fill-thread count, and `SyncGenerationPolicy.LOW_WATERMARK` from configuration. A request for an encrypted key first asks `ValueQueue` for the next cached value. If the queue needs refill, the refiller generates new encrypted keys through the underlying provider. `ExecutionException` from the queue is translated to `IOException`; `GeneralSecurityException` during refill is also wrapped as `IOException`.

Key version rollover and cache invalidation first perform the delegate operation via `super`, then drain cached encrypted keys for the named key. The comment explicitly notes that asynchronous refill can still race and produce old-version encrypted keys after a drain, but this is accepted because old key versions can still decrypt.

## State And Persistence
Persistent key material remains in the underlying key provider. This class adds transient in-memory per-key queues of encrypted key versions, background refill threads managed by `ValueQueue`, and cache expiry/low-watermark behavior. Drains clear cached values but do not affect stored keys.

## Dependencies And Integration Points
It depends on Hadoop `Configuration`, `KeyProviderCryptoExtension`, `ValueQueue`, and KMS server integration that wraps configured key providers. It is part of KMS encrypted-key generation performance behavior and interacts with key rollover, cache invalidation, decrypt, and reencrypt paths.

## Risks
The cache can serve old-version encrypted keys after rollover because async refill can race with drain. This is intentional but important for clients that might assume rollover immediately changes generated key versions. Cache size/fill threads affect memory, key-provider load, and latency. Wrapping security exceptions as IO exceptions can obscure root cause unless callers inspect causes. Background refill behavior must be thread-safe and bounded.

## Test Signals
Tests should cover cache warmup, low-watermark refill, default and configured cache parameters, propagation/wrapping of generation failures, direct delegation of decrypt/reencrypt, and drain after `rollNewVersion` or `invalidateCache`. Rollover tests should allow old-version encrypted keys while verifying decryptability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/EagerKeyGeneratorKeyProviderCryptoExtension.java -->
