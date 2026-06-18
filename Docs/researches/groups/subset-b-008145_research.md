# subset-b-008145 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestS3Utils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestS3Utils.java

## Purpose
JUnit 5 coverage for `S3Utils`, especially S3 storage-class-to-Ozone replication resolution, canonical user id generation, and Content-MD5 validation. It guards the S3 gateway contract that AWS-facing headers map to the correct Ozone replication settings and S3 error codes.

## Important APIs, types, and functions
The test drives `S3Utils.resolveS3ClientSideReplicationConfig`, `generateCanonicalUserId`, and `validateContentMD5`. It uses `S3StorageType`, `ECReplicationConfig`, `RatisReplicationConfig`, `ReplicationConfig`, `S3Owner`, `OS3Exception`, and `S3ErrorTable`. Parameter sources enumerate storage types, storage configs, client configs, and bucket configs.

## Control flow
Valid replication tests build the Cartesian product of allowed S3 storage type/config values and client/bucket defaults, call resolution, then independently compute expected precedence: S3 storage class overrides client and bucket config, client overrides bucket, and empty input returns null. Invalid tests expect `INVALID_STORAGE_CLASS`. MD5 tests compute valid and invalid client/server digests and assert either success or `INVALID_DIGEST`/`BAD_DIGEST`.

## State and persistence behavior
No persistent state is written. The only state is generated test data: replication config instances and digest encodings. Equality of replication objects is the key state signal.

## Dependencies and integration points
This file sits between S3 gateway request parsing and Ozone replication internals. It depends on HDDS replication config types, Apache Commons Hex/StringUtils, Java `MessageDigest`/Base64, and S3 error translation.

## Risks and edge cases
Coverage is intentionally combinatorial for valid replication inputs but only checks two invalid cases. Storage-class precedence or default EC policy changes will require expected-value updates. MD5 checks cover malformed Base64, wrong length, missing value, and mismatched digest.

## Test signals
Signals are exact replication object equality/nullness, canonical owner id equality, and precise S3 error code assertions for digest and storage-class failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestS3Utils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3secret/TestSecretGenerate.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3secret/TestSecretGenerate.java

## Purpose
Unit tests for the S3 secret generation REST endpoint. It verifies both self-service generation from the request security principal and explicit username generation.

## Important APIs, types, and functions
The test constructs `S3SecretManagementEndpoint` with an `OzoneClientStub`, `ObjectStoreStub`, and mocked `ClientProtocol`. It observes `S3SecretResponse`, JAX-RS `Response`, `ContainerRequestContext`, `UriInfo`, `SecurityContext`, `Principal`, `S3SecretValue`, and `OMException.ResultCodes.S3_SECRET_ALREADY_EXISTS`.

## Control flow
`setUp` creates request parameter maps and injects a stub client/context into the endpoint. `setupSecurityContext` wires principal name lookup. Success stubs `proxy.getS3Secret` to return `S3SecretValue.of(requestedUser, USER_SECRET)`. Existing-secret flow stubs the proxy to throw an OMException and expects a `BAD_REQUEST` status with the OM result code as reason phrase.

## State and persistence behavior
No real OM metadata is persisted. Secret state is simulated entirely by the mocked protocol response or exception. The endpoint is expected to project that state into HTTP response shape.

## Dependencies and integration points
This test covers the S3 secret management endpoint boundary with Ozone client protocol, JAX-RS request context, and OM exception-to-HTTP mapping.

## Risks and edge cases
It does not test null principals, authorization, multiple query/path params, or random secret generation internals. The helper returns a fixed secret, so cryptographic behavior is out of scope.

## Test signals
Signals are generated response access key/secret fields and HTTP `400` status plus reason phrase when a secret already exists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3secret/TestSecretGenerate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3secret/TestSecretRevoke.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3secret/TestSecretRevoke.java

## Purpose
Unit tests for the S3 secret revocation REST endpoint. It verifies principal-derived and explicit-user revocation plus endpoint status mapping for repeated or failed revokes.

## Important APIs, types, and functions
The test drives `S3SecretManagementEndpoint.revoke()` and `revoke(String)`. It mocks `ObjectStoreStub.revokeS3Secret`, JAX-RS request context objects, and uses `OMException.ResultCodes.S3_SECRET_NOT_FOUND` and `ACCESS_DENIED`.

## Control flow
`setUp` injects a stub Ozone client wrapping a mocked object store and an empty request URI context. Self-service tests mock the security principal, call `revoke`, and verify the object store is called with the principal name. Explicit revoke bypasses the security context. Sequential revoke first succeeds, then makes the object store throw `S3_SECRET_NOT_FOUND`; generic OM failure uses `ACCESS_DENIED`.

## State and persistence behavior
No persistent state is mutated. The only state transition is simulated by changing the mock from success to throwing after the first call.

## Dependencies and integration points
The test guards endpoint integration with `ObjectStore.revokeS3Secret`, security principal lookup, and REST status conversion.

## Risks and edge cases
Only selected OM exceptions are covered. Authorization semantics and real OM secret table persistence are not exercised.

## Test signals
Signals include Mockito call counts/arguments and HTTP statuses: `OK` on success, `NOT_FOUND` for missing secret, and `INTERNAL_SERVER_ERROR` for access-denied-style failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3secret/TestSecretRevoke.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/resources/groupAccessControlList.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/resources/groupAccessControlList.xml

## Purpose
XML fixture for S3 ACL parsing tests that include a mix of canonical user, group, email, and owner grants.

## Important APIs, types, and functions
The document uses the S3 `AccessControlPolicy` schema namespace, with `Owner`, `AccessControlList`, `Grant`, `Grantee`, and `Permission` elements. Grantee `xsi:type` values include `CanonicalUser`, `Group`, and `AmazonCustomerByEmail`.

## Control flow
Consumers parse owner metadata, then process five grants: owner full control, AllUsers read, LogDelivery write, AmazonCustomerByEmail write ACL, and another canonical user read ACL.

## State and persistence behavior
It is static test data, not persisted application state. It represents serialized ACL state as it would arrive over S3-compatible XML APIs.

## Dependencies and integration points
The fixture integrates S3 gateway XML binding/parsing with ACL conversion logic and namespace handling, including nested elements that reset XML namespace to empty.

## Risks and edge cases
Mixed grantee types and namespace overrides are the main edge cases. Email grantees may be unsupported by Ozone logic, so tests using this fixture likely assert rejection or partial interpretation.

## Test signals
Useful signals are parsed grant count, grantee type recognition, owner canonical id/display name, and permission mapping for group and user ACLs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/resources/groupAccessControlList.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/resources/userAccessControlList.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/resources/userAccessControlList.xml

## Purpose
XML fixture for S3 ACL parsing tests focused on canonical-user grants.

## Important APIs, types, and functions
The file is an S3 `AccessControlPolicy` document with an `Owner` and two `Grant` entries. Both grantees are `CanonicalUser`; permissions are `FULL_CONTROL` for the owner and `READ_ACP` for a second account.

## Control flow
Consumers parse the owner first, then iterate the ACL grants and map canonical IDs to Ozone/S3 ACL entries. The first owner ID intentionally spans whitespace/newline content inside the `ID` element.

## State and persistence behavior
Static serialized test state only. It models request/response XML used by S3 ACL APIs.

## Dependencies and integration points
This fixture exercises XML namespace handling, canonical user parsing, and permission translation in the S3 gateway.

## Risks and edge cases
Whitespace around canonical IDs can expose parsers that fail to trim or normalize element text. It does not include groups, emails, invalid permissions, or malformed XML.

## Test signals
Expected signals are correct owner extraction, two recognized grants, canonical-user grantee handling, and `FULL_CONTROL`/`READ_ACP` permission mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/resources/userAccessControlList.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/dev-support/findbugsExcludeFile.xml

## Purpose
SpotBugs exclusion filter for the `ozone-tools` module.

## Important APIs, types, and functions
The XML uses `FindBugsFilter` with `Match`, `Class`, and `Bug` pattern entries. It suppresses `OBL_UNSATISFIED_OBLIGATION_EXCEPTION_EDGE` for `TestReconUtils`, plus `RV_RETURN_VALUE_IGNORED_BAD_PRACTICE` and `DLS_DEAD_LOCAL_STORE` for `TestGenerateOzoneRequiredConfigurations`.

## Control flow
Maven SpotBugs reads this file from the module POM and excludes matching findings during analysis.

## State and persistence behavior
No runtime state. It persists static quality-gate policy for known test-code findings.

## Dependencies and integration points
Integrated via `spotbugs-maven-plugin` in `tools/pom.xml`.

## Risks and edge cases
Suppressions can mask real regressions if class names are reused or test behavior changes. One class, `TestReconUtils`, appears outside the visible tools test paths, so the filter may contain legacy or cross-module residue.

## Test signals
The signal is build/static-analysis success without these specific warnings failing the module.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/pom.xml

## Purpose
Maven module descriptor for `ozone-tools`, packaging CLI utilities such as Ozone FS shell, getconf, genconf, local runtime config, Ratis shell wrapper, logging, and completion support.

## Important APIs, types, and functions
Defines artifact `org.apache.ozone:ozone-tools:2.3.0-SNAPSHOT`, jar packaging, dependencies on Hadoop common, HDDS CLI/config/common, Ozone common/filesystem, Ratis common/shell/proto, picocli, Reflections, reload4j, JAXB, and test jars. Build plugins configure SpotBugs, annotation processors, and enforcer import restrictions.

## Control flow
During build, compiler processors generate MetaInfServices and picocli native-image metadata. SpotBugs consumes the module exclude filter. Enforcer overrides root banned imports and restricts selected annotation-related imports.

## State and persistence behavior
The POM controls produced artifacts and generated metadata, not runtime persistence. Runtime-scoped dependencies shape the classpath for shell execution.

## Dependencies and integration points
It ties tools code to HDDS/Ozone libraries, Hadoop FsShell, Ratis shell, and CLI registration infrastructure.

## Risks and edge cases
Dependency scopes are important: moving runtime dependencies to compile or removing annotation processors can break service discovery/autocomplete/native metadata. Enforcer bans protect layering around config annotations and OM validation annotations.

## Test signals
Signals are successful Maven compile/test/static-analysis runs and availability of expected CLI classes in the assembled classpath.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/fs/ozone/OzoneFsDelete.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/fs/ozone/OzoneFsDelete.java

## Purpose
Ozone-specific delete command registrations and implementations for Hadoop FsShell, overriding standard `-rm` behavior where Ozone symlink and URI semantics differ.

## Important APIs, types, and functions
`registerCommands` binds `-rm` and `-rmr`. `Rm` extends `FsCommand` and implements option parsing, argument expansion, path processing, trash handling, and safe-delete prompts. `Rmr` prepends `-r` and reports replacement command `-rm -r`.

## Control flow
`processOptions` parses `-f`, `-r`, `-R`, `-skipTrash`, and `-safely`. `expandArgument` records trailing slash and suppresses missing paths under `-f`. `processPath` detects symlinks, rejects directories without recursion, preserves Ozone trailing-slash behavior for symlink bucket contents, tries Trash unless skipped, optionally confirms large recursive deletes, then calls `FileSystem.delete`.

## State and persistence behavior
The command mutates filesystem namespace state by moving paths to Trash or deleting them. It reads content summary for safety checks and consults Hadoop delete-limit configuration.

## Dependencies and integration points
Integrates Hadoop shell classes, `Trash`, `PathData`, `ContentSummary`, Ozone URI delimiter semantics, and `ToolRunner.confirmPrompt`.

## Risks and edge cases
The `trailing` flag is command-instance state and can affect later paths after any trailing-slash argument. Symlink detection depends on `getLinkTarget(item.path) != item.path`, which is object-identity-sensitive. Trash failures are rewrapped with `-skipTrash` guidance.

## Test signals
Direct tests in this subset check command registration. Behavioral signals would include directory rejection, missing-file `-f`, trash fallback, safe-delete prompt behavior, and symlink trailing slash deletes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/fs/ozone/OzoneFsDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/fs/ozone/OzoneFsShell.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/fs/ozone/OzoneFsShell.java

## Purpose
Ozone-specific `FsShell` entry point backing `ozone fs` commands.

## Important APIs, types, and functions
Extends Hadoop `FsShell`, registers default `FsCommand` classes and then `OzoneFsDelete`, customizes usage prefix, initializes tracing, and exposes `getCommandFactory` for tests.

## Control flow
`main` creates an `OzoneConfiguration`, initializes tracing, sets quiet mode false, installs the config, wraps `ToolRunner.run` inside `TracingUtil.executeInNewSpan`, and exits with the shell result. Command registration only happens when the runtime class is exactly `OzoneFsShell`.

## State and persistence behavior
No persistent state is owned by the shell. It configures runtime command registry and tracing span state, and commands may mutate filesystem state.

## Dependencies and integration points
Integrates Hadoop FsShell/ToolRunner, HDDS tracing, Ozone configuration, and the Ozone delete override.

## Risks and edge cases
Exact-class registration guard can surprise subclasses. `System.exit` in `main` makes direct invocation unsuitable for embedded tests. Span naming concatenates user args into tracing data.

## Test signals
`TestOzoneFsShell` confirms `-rm` resolves to `OzoneFsDelete.Rm` and command metadata is available after shell execution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/fs/ozone/OzoneFsShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/fs/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/fs/ozone/package-info.java

## Purpose
Package documentation for Ozone customizations of Hadoop FS CLI.

## Important APIs, types, and functions
Declares package `org.apache.hadoop.fs.ozone`. No executable APIs are defined.

## Control flow
No control flow.

## State and persistence behavior
No state or persistence behavior.

## Dependencies and integration points
Documents the package containing `OzoneFsShell` and `OzoneFsDelete`.

## Risks and edge cases
Risk is limited to stale package description if the package grows beyond CLI customizations.

## Test signals
No direct tests; compile/package documentation generation is the signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/fs/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/OzoneGetConf.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/OzoneGetConf.java

## Purpose
Picocli-based `ozone getconf` command for printing selected Ozone configuration values and service host lists.

## Important APIs, types, and functions
Extends `GenericCli`, exposes helper methods `printError`, `printOut`, and package-private `getConf`, and registers subcommands `PrintConfKeyCommandHandler`, `StorageContainerManagersCommandHandler`, and `OzoneManagersCommandHandler`.

## Control flow
`main` resets log4j configuration to concise console output, suppresses native-code loader noise, then executes the CLI through `GenericCli.run`.

## State and persistence behavior
Reads current `OzoneConfiguration`; does not persist or mutate config. It mutates process logging setup.

## Dependencies and integration points
Integrates HDDS `GenericCli`, picocli, `HddsVersionProvider`, `OzoneConfiguration`, and log4j/reload4j.

## Risks and edge cases
Package-private helper methods ease testing but keep command handlers tightly coupled to the parent class. Logging reset is global and can affect embedded callers.

## Test signals
`TestGetConfOptions` captures stdout for `confKey`, `storagecontainermanagers`, and `ozonemanagers` aliases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/OzoneGetConf.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/OzoneManagersCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/OzoneManagersCommandHandler.java

## Purpose
Subcommand handler for `ozone getconf ozonemanagers` and `-ozonemanagers`, printing configured OM host names.

## Important APIs, types, and functions
Implements `Callable<Void>`, uses parent `OzoneGetConf`, `OzoneConfiguration.of`, `OmUtils.isServiceIdsDefined`, `getOmHAAddressesById`, and `OmUtils.getOmAddress`.

## Control flow
On call, it wraps the parent config as a `ConfigurationSource`. If OM service IDs are defined, it flattens all HA service address collections and prints each host name. Otherwise it prints the singleton OM address host name.

## State and persistence behavior
Read-only configuration inspection; no persistence.

## Dependencies and integration points
Connects the getconf CLI to OM HA/single-node address parsing in `OmUtils`.

## Risks and edge cases
For HA services, it prints all service addresses without filtering to a selected service. Host names are printed without ports, and unresolved/empty configurations may produce blank output or upstream exceptions.

## Test signals
Tests set a service ID without node addresses and assert empty output for both alias forms, confirming current handling of incomplete HA config.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/OzoneManagersCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/PrintConfKeyCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/PrintConfKeyCommandHandler.java

## Purpose
Subcommand handler for printing one trimmed configuration key value.

## Important APIs, types, and functions
Uses picocli `@Parameters(arity="1..1")`, parent `OzoneGetConf`, and `OzoneConfiguration.getTrimmed`.

## Control flow
`call` reads the named key. If present, it prints the trimmed value through the parent output method; if absent, it throws `IllegalArgumentException`.

## State and persistence behavior
Read-only config access. No state persists.

## Dependencies and integration points
Part of the `ozone getconf` command tree and GenericCli error handling.

## Risks and edge cases
Empty strings may be treated as present because only null is rejected. The thrown exception message is user-facing through picocli/GenericCli.

## Test signals
`TestGetConfOptions` asserts both `-confKey` and `confKey` forms print configured SCM names and OM node id.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/PrintConfKeyCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/StorageContainerManagersCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/StorageContainerManagersCommandHandler.java

## Purpose
Subcommand handler for `ozone getconf storagecontainermanagers`, printing SCM host names used by clients.

## Important APIs, types, and functions
Implements `Callable<Void>`, uses `HddsUtils.getScmAddressForClients`, parent `OzoneGetConf`, and `OzoneConfiguration.of`.

## Control flow
On invocation, it resolves client-facing SCM addresses from the current config and prints the host name for each `InetSocketAddress`.

## State and persistence behavior
Read-only config lookup; no persistence.

## Dependencies and integration points
Connects getconf output to HDDS SCM client address resolution.

## Risks and edge cases
Ports are omitted. Multiple SCM addresses print one per line. Invalid SCM configuration errors are delegated to `HddsUtils`.

## Test signals
Tests set `ozone.scm.names` to localhost and assert both alias forms print `localhost`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/StorageContainerManagersCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/package-info.java

## Purpose
Package documentation for Ozone getconf tool classes.

## Important APIs, types, and functions
Declares package `org.apache.hadoop.ozone.conf`.

## Control flow
No executable flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Documents the package containing `OzoneGetConf` and its command handlers.

## Risks and edge cases
Only stale documentation risk.

## Test signals
Compilation is the only direct signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/genconf/GenerateOzoneRequiredConfigurations.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/genconf/GenerateOzoneRequiredConfigurations.java

## Purpose
CLI tool for generating a minimal `ozone-site.xml` template from `ozone-default.xml`, optionally including Kerberos/security properties.

## Important APIs, types, and functions
Extends `GenericCli`, implements `Callable<Void>`, uses JAXB marshalling of `OzoneConfiguration.XMLConfiguration`, reads `OzoneConfiguration.Property` entries, and has helpers `isValidPath` and `canWrite`.

## Control flow
`call` delegates to `generateConfigurations`. The method validates the target directory and write permission, loads `ozone-default.xml`, selects properties tagged `REQUIRED` plus `KERBEROS` when `--security` is set, populates defaults for metadata dir, OM/SCM addresses, and security-related values, then creates `ozone-site.xml` only if it does not already exist.

## State and persistence behavior
Persists a new XML config file in the target directory. It intentionally avoids overwriting existing `ozone-site.xml`.

## Dependencies and integration points
Integrates config metadata from Ozone defaults, constants from Ozone/OM/SCM keys, JAXB XML serialization, picocli, and filesystem permissions.

## Risks and edge cases
`File.canWrite` can behave differently under elevated users or platform ACLs. The selection depends on accurate config tags in `ozone-default.xml`. Existing file handling is non-atomic.

## Test signals
Tests verify generation, non-empty values, security mode adds properties, no overwrite, invalid path, insufficient permission, missing parameter, and help output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/genconf/GenerateOzoneRequiredConfigurations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/genconf/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/genconf/package-info.java

## Purpose
Package documentation for the Ozone required-configuration generator.

## Important APIs, types, and functions
Declares package `org.apache.hadoop.ozone.genconf`.

## Control flow
No executable behavior.

## State and persistence behavior
No state; related package tool writes `ozone-site.xml`.

## Dependencies and integration points
Documents package ownership for `GenerateOzoneRequiredConfigurations`.

## Risks and edge cases
Only stale package comment risk.

## Test signals
Compile/package documentation generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/genconf/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/LocalOzoneClusterConfig.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/LocalOzoneClusterConfig.java

## Purpose
Immutable configuration model for an internal local Ozone cluster runtime.

## Important APIs, types, and functions
Defines defaults for data directory, format mode, datanode count, host/bind host, service ports, S3 gateway, ephemeral cleanup, startup timeout, and local S3 credentials. Exposes getters, `builder()`, `builder(Path)`, `FormatMode`, and a fluent `Builder`.

## Control flow
Builder methods collect values; `build` constructs an immutable config, normalizing the data directory and null-checking object fields. `FormatMode.fromString` trims, uppercases, converts hyphens to underscores, and delegates to enum lookup.

## State and persistence behavior
No runtime persistence. The config describes future runtime state such as storage formatting and whether data should be removed on shutdown.

## Dependencies and integration points
Consumed by `OzoneLocal.RunCommand` and the `LocalOzoneRuntime` contract. Defaults are mirrored as string constants for picocli annotation defaults.

## Risks and edge cases
Builder does not validate ranges; validation is in CLI code. Null setter values fail at build time. Default local credentials are only suitable for local/demo use.

## Test signals
Tests verify defaults, string defaults matching typed defaults, explicit overrides, and format-mode parsing/rejection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/LocalOzoneClusterConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/LocalOzoneRuntime.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/LocalOzoneRuntime.java

## Purpose
Interface defining lifecycle and endpoint contract for a local Ozone cluster runtime.

## Important APIs, types, and functions
Extends `AutoCloseable`. Methods include `start`, `getDisplayHost`, `getScmPort`, `getOmPort`, `getS3gPort`, `getS3Endpoint`, and `close`.

## Control flow
Implementations must start services before endpoint accessors return usable values and must release resources in `close`.

## State and persistence behavior
The interface does not own state. Implementations may create persistent or ephemeral local cluster data depending on `LocalOzoneClusterConfig`.

## Dependencies and integration points
Defines the seam between CLI configuration resolution and a concrete local Ozone service launcher.

## Risks and edge cases
No implementation is present in this subset, so startup readiness, cleanup, and endpoint consistency depend on external implementers.

## Test signals
No direct tests in this subset; compile-time implementability is the signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/LocalOzoneRuntime.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/OzoneLocal.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/OzoneLocal.java

## Purpose
Hidden internal CLI entry point `ozone local` with a hidden `run` command that resolves local cluster runtime configuration.

## Important APIs, types, and functions
Extends `GenericCli`. `RunCommand` extends `AbstractSubcommand`, declares options with environment-variable defaults, and resolves a `LocalOzoneClusterConfig`. Nested converters parse `FormatMode` and ISO/Hadoop-style `Duration`.

## Control flow
CLI default values first consult `OZONE_LOCAL_*` environment variables. `RunCommand.call` resolves config quietly. `resolveConfig` validates datanodes >= 1, ports 0..65535, and positive startup timeout, then builds the immutable config.

## State and persistence behavior
No runtime cluster is started here and no persistent state is written. The command only materializes config state for a future runtime.

## Dependencies and integration points
Uses picocli, HDDS `GenericCli`/`AbstractSubcommand`, `TimeDurationUtil`, and `LocalOzoneClusterConfig`.

## Risks and edge cases
Command is hidden, so user-facing stability may be lower. Environment default expressions are duplicated across many constants and tested reflectively. Invalid data-dir parse uses picocli path conversion.

## Test signals
Tests cover hidden metadata, subcommand registration, help hiding, quiet run, env default strings, CLI overrides, duration parsing, negatable booleans, invalid ports/datanodes/durations/paths, legacy option rejection, and error output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/OzoneLocal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/package-info.java

## Purpose
Package documentation for internal local Ozone cluster runtime support.

## Important APIs, types, and functions
Declares package `org.apache.hadoop.ozone.local`.

## Control flow
No executable behavior.

## State and persistence behavior
No state.

## Dependencies and integration points
Documents the package containing local cluster config, runtime contract, and hidden CLI.

## Risks and edge cases
Only stale documentation risk.

## Test signals
Compile/package documentation generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/local/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/shell/OzoneRatis.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/shell/OzoneRatis.java

## Purpose
Wrapper command `ozone ratis` that delegates to Apache Ratis shell under Ozone CLI/tracing infrastructure.

## Important APIs, types, and functions
Extends `GenericCli`, overrides `execute`, initializes `TracingUtil`, creates `RatisShell`, and runs argv through it.

## Control flow
`main` invokes GenericCli. `execute` initializes tracing with the current Ozone config, creates a span named from the command arguments, constructs `RatisShell(System.out)`, and returns its exit code.

## State and persistence behavior
No persistent state. Ratis subcommands may read/write files depending on arguments, as shown by raft-meta-conf tests.

## Dependencies and integration points
Integrates Ozone CLI command discovery with Ratis shell commands. A TODO notes future use of RatisShell.Builder for TLS/conf support.

## Risks and edge cases
Current shell construction does not wire Ozone TLS or other configs into Ratis. Span name lacks a space between `ratis` and joined args.

## Test signals
Tests verify base usage output and local raft-meta-conf subcommand behavior, including generated protobuf file content and parse errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/shell/OzoneRatis.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/shell/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/shell/package-info.java

## Purpose
Package documentation for Ozone shell classes.

## Important APIs, types, and functions
Declares package `org.apache.hadoop.ozone.shell`.

## Control flow
No executable flow.

## State and persistence behavior
No state.

## Dependencies and integration points
Documents the package containing `OzoneRatis` and related shell entry points.

## Risks and edge cases
The comment is broad and may become stale as command set changes.

## Test signals
Compilation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/shell/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/utils/AsyncRollingFileAppender.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/utils/AsyncRollingFileAppender.java

## Purpose
Log4j appender that lazily wraps a `RollingFileAppender` inside an `AsyncAppender`.

## Important APIs, types, and functions
Extends `AsyncAppender`, overrides `append`, and exposes synchronized getters/setters for max file size, backup index, file name, conversion pattern, blocking, and buffer size.

## Control flow
On first append, if no rolling appender exists, `createRollingFileAppender` synchronizes, builds a `PatternLayout`, creates a file appender in append mode, sets rolling limits, adds it to the async appender, then applies deferred blocking and buffer-size settings.

## State and persistence behavior
Persists log events to the configured file and rotates by max size/index. Configuration values are stored until first append.

## Dependencies and integration points
Uses reload4j/log4j `AsyncAppender`, `RollingFileAppender`, `PatternLayout`, and `LoggingEvent`.

## Risks and edge cases
Missing `fileName` causes runtime appender creation failure. Settings changed after the rolling appender is assigned may not propagate to the underlying appender. IOException is converted to unchecked `RuntimeException`.

## Test signals
No direct test in this subset. Signals would be log file creation, async buffering behavior, and rolling under configured size limits.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/utils/AsyncRollingFileAppender.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/utils/AutoCompletion.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/utils/AutoCompletion.java

## Purpose
CLI command `ozone completion` for generating shell completion scripts for Ozone commands.

## Important APIs, types, and functions
Extends `GenericCli`, has `bash` and `zsh` subcommands, scans configured packages with Reflections for `GenericCli` subclasses, instantiates their picocli command models, filters public commands, and calls `AutoComplete.bash`.

## Control flow
`getBashCompletion` creates a synthetic top-level `ozone` command with common wrapper options, discovers command classes under HDDS/Ozone packages, adds public subcommands by stripping an `ozone ` prefix, and returns generated bash completion. Zsh currently emits the same bash script.

## State and persistence behavior
No persistent state. It performs runtime classpath scanning and writes generated script text to stdout.

## Dependencies and integration points
Integrates picocli autocomplete, HDDS GenericCli command metadata, Reflections classpath scanning, and Ratis `ReflectionUtils` instantiation.

## Risks and edge cases
Classpath scanning can be slow or incomplete depending on packaging. Commands without no-arg constructors are skipped. Zsh behavior may be bash-compatible rather than native zsh.

## Test signals
No direct tests here. Useful signals are generated script containing expected public commands and excluding hidden/default-name commands.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/utils/AutoCompletion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/utils/package-info.java

## Purpose
Package documentation for Ozone utility classes in the tools module.

## Important APIs, types, and functions
Declares package `org.apache.hadoop.ozone.utils`.

## Control flow
No executable flow.

## State and persistence behavior
No state.

## Dependencies and integration points
Documents package containing completion and logging utility classes.

## Risks and edge cases
Only stale package comment risk.

## Test signals
Compilation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/java/org/apache/hadoop/fs/ozone/TestOzoneFsShell.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/java/org/apache/hadoop/fs/ozone/TestOzoneFsShell.java

## Purpose
Unit test verifying `OzoneFsShell` registers the Ozone-specific delete command override.

## Important APIs, types, and functions
Uses `OzoneFsShell`, Hadoop `ToolRunner`, `CommandFactory`, `Command`, and `OzoneFsDelete.Rm`. Captures stderr to keep failed shell parse output from polluting test output.

## Control flow
The test runs the shell with invalid dummy arguments to trigger command registration, obtains the command factory, asserts a single `-rm` binding, instantiates it, and checks class and command name.

## State and persistence behavior
No filesystem state is modified; command execution is only used to initialize the registry. System stderr is temporarily redirected and restored.

## Dependencies and integration points
Tests OzoneFsShell integration with Hadoop FsShell command factory and Ozone delete override ordering.

## Risks and edge cases
It does not test actual delete behavior or every registered command. The source path contains `src/test/java/java`, which is unusual but valid if included by build configuration.

## Test signals
Factory non-nullness, exactly one `-rm` command name, instance class `OzoneFsDelete.Rm`, and command name `rm`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/java/org/apache/hadoop/fs/ozone/TestOzoneFsShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/conf/TestGetConfOptions.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/conf/TestGetConfOptions.java

## Purpose
Tests command aliases and output behavior for `ozone getconf`.

## Important APIs, types, and functions
Uses `OzoneGetConf`, `GenericTestUtils.PrintStreamCapturer`, SCM and OM config keys, and `IOUtils.closeQuietly`.

## Control flow
Static setup captures stdout, creates one command instance, and sets OM node id, OM service ID, and SCM names. Each test runs alias and non-alias forms, resets captured output, and asserts exact strings.

## State and persistence behavior
Mutates only in-memory `OzoneConfiguration` on the command object and process stdout capture state.

## Dependencies and integration points
Tests picocli subcommand aliases for conf key, SCM host listing, and OM host listing.

## Risks and edge cases
The same command instance is shared across tests; output reset avoids leakage but config persists intentionally. OM manager output is asserted empty for incomplete HA config, which may change if validation behavior changes.

## Test signals
Exact stdout: `localhost` for SCM names, `1` for OM node id, and empty OM host listing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/conf/TestGetConfOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/genconf/TestGenerateOzoneRequiredConfigurations.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/genconf/TestGenerateOzoneRequiredConfigurations.java

## Purpose
Unit tests for the `ozone genconf` CLI, validating template creation, security expansion, no-overwrite behavior, errors, and help.

## Important APIs, types, and functions
Uses `GenerateOzoneRequiredConfigurations`, picocli `CommandLine.parseWithHandlers`, JUnit temp directories, `OzoneConfiguration.readPropertyFromXml`, AssertJ, and system stream capture.

## Control flow
Helpers execute picocli with handlers that rethrow parse/execution exceptions. Generation tests run CLI into temp directories, read the resulting `ozone-site.xml`, and assert all property values are non-empty. Security generation compares property counts. Failure tests invoke invalid path, read-only directory, missing path, and help.

## State and persistence behavior
Creates `ozone-site.xml` files under JUnit temp directories, temporarily replaces `System.out` and `System.err`, and restores them after each test.

## Dependencies and integration points
Tests JAXB output indirectly through OzoneConfiguration XML reading and picocli command parsing.

## Risks and edge cases
Read-only permission tests can be platform/user dependent. The helper catches any exception and asserts message content, so a missing exception could silently pass if not carefully inspected, although output assertions cover success cases.

## Test signals
Generated file exists with non-empty values, secure config count differs, overwrite message appears, and expected error/help substrings are present.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/genconf/TestGenerateOzoneRequiredConfigurations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/genconf/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/genconf/package-info.java

## Purpose
Package documentation for genconf tests.

## Important APIs, types, and functions
Declares package `org.apache.hadoop.ozone.genconf`.

## Control flow
No executable behavior.

## State and persistence behavior
No state.

## Dependencies and integration points
Documents test package for `GenerateOzoneRequiredConfigurations`.

## Risks and edge cases
Only stale documentation risk.

## Test signals
Compilation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/genconf/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/local/TestLocalOzoneClusterConfig.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/local/TestLocalOzoneClusterConfig.java

## Purpose
Unit tests for the local cluster configuration value object and format-mode parser.

## Important APIs, types, and functions
Uses `LocalOzoneClusterConfig`, its `Builder`, `FormatMode`, default constants, JUnit assertions, `Paths`, and `Duration`.

## Control flow
Tests build default and overridden configs, compare all getter values, verify string default constants parse to typed defaults, parse user-facing format mode values, and reject unknown/null modes.

## State and persistence behavior
No persistent state. Path defaults and overrides are normalized to absolute paths.

## Dependencies and integration points
Validates the model consumed by `OzoneLocal.RunCommand` and future local runtime implementations.

## Risks and edge cases
Does not cover null builder setters except format mode parser null. Numeric validation is intentionally tested in `TestOzoneLocal`, not here.

## Test signals
Exact values for data dir, mode, datanodes, hosts, ports, S3 defaults, timeout, and parser exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/local/TestLocalOzoneClusterConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/local/TestOzoneLocal.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/local/TestOzoneLocal.java

## Purpose
Unit tests for hidden `ozone local run` CLI metadata, defaults, parsing, validation, and GenericCli error output.

## Important APIs, types, and functions
Uses `OzoneLocal`, `RunCommand`, `LocalOzoneClusterConfig`, picocli `CommandLine`, reflective access to `@Option` default values, custom `IDefaultValueProvider`, and JUnit assertions.

## Control flow
Tests inspect command annotations, ensure GenericCli registers `run`, capture help output to verify hidden subcommand behavior, execute `run` with no output, validate every environment default expression, resolve defaults through a fallback provider, parse overrides, test ISO and Hadoop-style durations, exercise negatable booleans, and assert parse/config errors.

## State and persistence behavior
No persistent state. Tests mutate command-line parser output/error streams and instantiate command objects.

## Dependencies and integration points
Validates picocli integration with HDDS GenericCli and the `LocalOzoneClusterConfig` builder.

## Risks and edge cases
Reflection ties tests to field names. It does not verify actual environment-variable expansion values from a real environment.

## Test signals
Signals include exact metadata, hidden help behavior, resolved config values, thrown `ParameterException`/`IllegalArgumentException`, and GenericCli exit code `-1` for invalid config.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/local/TestOzoneLocal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneRatis.java -->
# sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneRatis.java

## Purpose
Tests the Ozone wrapper around Ratis shell, especially local raft-meta-conf rewriting behavior and argument validation.

## Important APIs, types, and functions
Uses `OzoneRatis`, Ratis protobuf `LogEntryProto`, `RaftPeerProto`, `RaftConfigurationProto`, JUnit temp directories, and captured system output/error.

## Control flow
Setup redirects stdout/stderr and creates an `OzoneRatis`. Basic test runs an empty command and checks usage. The raft-meta-conf test writes a protobuf `raft-meta.conf`, invokes `local raftMetaConf` with peer/path args, checks output text, confirms `new-raft-meta.conf` exists, parses it, and validates index and peer fields. Negative tests pass missing/invalid/duplicate peer args and check parse messages.

## State and persistence behavior
Writes temporary Ratis metadata files and generated replacement protobufs. System streams are temporarily replaced.

## Dependencies and integration points
Tests OzoneRatis delegation to Ratis shell local commands and protobuf file compatibility.

## Risks and edge cases
Output message assertions can be brittle across Ratis upgrades. The wrapper does not validate TLS/config integration.

## Test signals
Usage text, generated protobuf index increment, peer id/address/startup role, and exact parse/duplicate error substrings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneRatis.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/dev-support/findbugsExcludeFile.xml

## Purpose
SpotBugs exclusion filter for the `ozone-vapor` module.

## Important APIs, types, and functions
Defines an empty `FindBugsFilter`.

## Control flow
SpotBugs reads the file during Maven analysis but no findings are excluded.

## State and persistence behavior
No runtime state.

## Dependencies and integration points
Referenced by the `spotbugs-maven-plugin` configuration in `vapor/pom.xml`.

## Risks and edge cases
An empty filter keeps the module strict, but future suppressions must be added deliberately.

## Test signals
Static-analysis build passes without module-specific suppressions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/pom.xml

## Purpose
Maven module descriptor for `ozone-vapor`, server-side load and simulation tools built on Freon/Ozone internals.

## Important APIs, types, and functions
Defines artifact `org.apache.ozone:ozone-vapor`, dependencies on Jackson, protobuf, metrics, Hadoop common/HDFS, HTTP components, HDDS client/server/container/SCM modules, Ozone admin/common/freon/manager/interface storage, Ratis client/common/proto, picocli, and MetaInfServices. Build config mirrors tools module with SpotBugs, annotation processors, and enforcer import bans.

## Control flow
Compile runs service-registration and picocli native-image processors. SpotBugs reads the empty module filter. Enforcer restricts selected annotation imports.

## State and persistence behavior
No runtime state, but dependency graph enables Vapor commands that talk to SCM, datanodes, containers, and Ratis and may write local load-test data.

## Dependencies and integration points
This module intentionally integrates deeply with server internals rather than only public clients.

## Risks and edge cases
Broad internal dependencies increase coupling to implementation changes. Runtime tools can stress real clusters, so classpath and version alignment matter.

## Test signals
Build success, service-loader registration of `VaporSubcommand` implementations, and static-analysis success.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/BaseAppendLogGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/BaseAppendLogGenerator.java

## Purpose
Base class for Vapor append-log generators that target isolated Ratis datanode scenarios.

## Important APIs, types, and functions
Extends `BaseFreonGenerator` and implements `VaporSubcommand`. Defines CLI options for raft peer id, Ratis server address, and in-flight limit. Holds a `BlockingQueue<Long>` for in-flight message IDs and helper `setServerIdFromFile`.

## Control flow
`setServerIdFromFile` resolves the datanode ID file path from Ozone config. If CLI server id is blank and the file exists, it reads `DatanodeDetails` from YAML and uses its UUID. It then asserts a non-empty server id.

## State and persistence behavior
Reads datanode identity from local datanode ID YAML; does not write it. In-flight queue is owned by subclasses.

## Dependencies and integration points
Integrates Freon command infrastructure, HDDS server utility paths, datanode ID YAML parsing, Ratis preconditions, and picocli options.

## Risks and edge cases
Fails fast when no id is supplied and no local datanode ID file exists. Server address and id defaults are aimed at local standalone tests.

## Test signals
No direct tests here; subclass startup success/failure provides coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/BaseAppendLogGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/ChunkManagerDiskWrite.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/ChunkManagerDiskWrite.java

## Purpose
Vapor/Freon load generator that writes chunks directly through datanode `ChunkManager` to benchmark local disk/container write paths.

## Important APIs, types, and functions
Command `cmdw`/`chunk-manager-disk-write`, options for chunk size, chunks per block, and container layout. Uses `MutableVolumeSet`, `RoundRobinVolumeChoosingPolicy`, `KeyValueContainer`, `KeyValueContainerData`, `ChunkManagerFactory`, `DispatcherContext`, `BlockID`, `ChunkInfo`, Dropwizard `Timer`, and Freon `runTests`.

## Control flow
`call` initializes Freon, creates one fresh key-value container per worker thread, computes block size, generates random payload data, creates a chunk manager, then runs `writeChunk`. Each operation derives thread id from thread name, selects that thread’s container, computes offset/local block id from thread-local bytes written, builds dispatcher context, wraps the shared data in a `ByteBuffer`, and times `writeChunk`.

## State and persistence behavior
Creates container directories/data on configured datanode volumes and writes chunk files or layout-specific data. Thread-local counters track per-thread block offsets.

## Dependencies and integration points
Exercises datanode storage volume selection, key-value container layout, chunk manager implementation, Freon metrics, and container write-state-machine context.

## Risks and edge cases
Thread id parsing depends on pool thread naming. Random container IDs can collide rarely. Shared byte array is safe, but per-operation `ByteBuffer.wrap` is needed for independent position. Containers are not explicitly cleaned.

## Test signals
No direct tests. Runtime signals are Freon operation counts, `chunk-write` timer, and absence of `StorageContainerException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/ChunkManagerDiskWrite.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/ClosedContainerReplicator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/ClosedContainerReplicator.java

## Purpose
Vapor command that downloads/imports closed containers using datanode replication code, mainly for replication performance and behavior testing.

## Important APIs, types, and functions
Command `cr`/`container-replicator`, option `--datanode`. Uses `ContainerOperationClient`, `ContainerInfo`, `Pipeline`, `ReplicationTask`, `ReplicateContainerCommand`, `ReplicationSupervisor`, `DownloadAndImportReplicator`, `ContainerImporter`, `SimpleContainerDownloader`, `ContainerSet`, handlers, volume sets, container metadata store, and metrics timer.

## Control flow
`replicate` validates destination storage directories are empty, lists up to one million containers from SCM, initializes a fake datanode replication supervisor/controller/importer stack, builds tasks for closed containers optionally filtered by source datanode UUID, sets Freon test count to task count, then runs each task through `ReplicationSupervisor.TaskRunner`.

## State and persistence behavior
Writes imported container data into configured datanode storage directories and opens a witnessed container metadata store. It refuses non-empty destination directories to avoid clobbering existing data.

## Dependencies and integration points
Deeply integrates SCM container listing/pipelines, datanode volume initialization, schema V3 DB loading, container handlers, replication downloader/importer, and Freon metrics.

## Risks and edge cases
Destination emptiness is mandatory. Queue size is based on container count. Fake datanode IDs and random SCM/cluster IDs may affect metadata compatibility. Only CLOSED containers are replicated.

## Test signals
No direct tests. Signals are task count, `replicate-container` timing, successful imports, and supervisor counters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/ClosedContainerReplicator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/DatanodeSimulationState.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/DatanodeSimulationState.java

## Purpose
Mutable state model for one simulated datanode used by Vapor’s SCM/Recon stress simulator.

## Important APIs, types, and functions
Tracks `DatanodeDetails`, registration flag, endpoint-specific report state, pipelines, containers, readonly flag, full-container-report interval, and target container count. Builds heartbeat, node report, pipeline report, full container report, and incremental container reports. Includes Jackson serializers for `DatanodeDetails`.

## Control flow
`ackHeartbeatResponse` applies SCM commands: create pipeline unless readonly, close pipeline, and close container. `heartbeatRequest` builds a datanode heartbeat with node/pipeline reports and either a full report when due or pending ICRs. `newContainer` and `closeContainer` mutate container state and enqueue ICRs for every endpoint.

## State and persistence behavior
State is serialized to JSON by `DatanodeSimulator`, including datanode details, pipelines, containers, FCR duration, and target count. Endpoint ICR scheduling is runtime-only and reinitialized after reload.

## Dependencies and integration points
Uses HDDS protocol protobufs, container replica states, storage location reports, Jackson binary serialization for datanode details, and SCM command types.

## Risks and edge cases
Most methods synchronize except readonly setter. Report data uses synthetic fixed metrics. Full-report scheduling uses random initial delay to avoid spikes. Unknown close-container commands only log errors.

## Test signals
No direct tests. Observable signals are heartbeat contents, FCR/ICR counts, pipeline set mutations, and JSON reload compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/DatanodeSimulationState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/DatanodeSimulator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/DatanodeSimulator.java

## Purpose
Vapor command that simulates many datanodes registering to SCM/Recon, heartbeating, and growing synthetic container state for scale testing.

## Important APIs, types, and functions
Command `simulate-datanode`, options for heartbeat threads, node count, containers per node, and reload. Uses `DatanodeSimulationState`, SCM/Recon datanode protocol translators, `StorageContainerLocationProtocol`, Ratis/SCM container allocation, HDDS layout version, Hadoop RPC, retry policies, JSON utils, and scheduled executors.

## Control flow
`call` initializes clients/layout, loads or creates simulated datanodes, registers each to SCM/Recon, schedules heartbeat tasks to every endpoint, installs a shutdown hook to stop executors, close clients, and save state, starts periodic stats logging, allocates containers until target assignment count is reached, closes each created container, then marks simulated nodes readonly and closes their pipelines.

## State and persistence behavior
Persists simulator state to `datanode-simulation.json` under the Ozone metadata directory on shutdown and reloads it by default. Runtime heartbeats maintain counters for total heartbeats/FCRs/ICRs.

## Dependencies and integration points
Exercises SCM datanode registration/heartbeat, Recon heartbeat, SCM container allocation/close APIs, layout storage/version manager, Hadoop protobuf RPC, HA SCM client creation, and Ozone metadata directory discovery.

## Risks and edge cases
Designed for stress environments and can create many SCM objects. Shutdown hook throws RuntimeException on interrupted await. Mixed real/simulated clusters may produce under-replicated synthetic containers. Random IPs may be unrealistic.

## Test signals
No direct tests. Runtime logs report registered node count, heartbeat/FCR/ICR rates, assigned container count, and readonly transition completion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/DatanodeSimulator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/FollowerAppendLogEntryGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/FollowerAppendLogEntryGenerator.java

## Purpose
Freon/Vapor generator that acts as a fake Ratis leader and streams append entries directly to an isolated follower datanode.

## Important APIs, types, and functions
Command `falg`, options for pipeline id, chunk size, batching, next index, and rate limit. Extends `BaseAppendLogGenerator` and implements gRPC `StreamObserver<AppendEntriesReplyProto>`. Uses Ratis gRPC stubs, group management, vote requests, append entries, Ozone `ContainerCommandRequestProto` write-chunk payloads, in-flight queue, and metrics timer.

## Control flow
`call` initializes payload, server id, fake leader peer, plaintext gRPC channel, optional rate limiter, Freon state, and append stream. If starting from index zero, it configures a two-peer group, requests a vote, sends an initial configuration log entry, then runs Freon operations that generate batched write-chunk log entries. Replies remove call IDs and warn when follower commit lags.

## State and persistence behavior
Mutates the target follower’s Ratis log and datanode chunk/container state through append entries. Maintains client-side `nextIndex`, in-flight call IDs, and optional rate limiter.

## Dependencies and integration points
Integrates Ratis server protocol gRPC, Ratis client group management, Ozone container protobuf commands, Freon metrics, and local datanode identity discovery.

## Risks and edge cases
Requires exactly one Freon thread. Uses plaintext and fake fixed IDs/addresses. Initial config peer id uses `serverAddress` in one place, which may not match UUID server id. Data is generated for testing, not secure randomness.

## Test signals
No direct tests. Signals are vote success, append replies, in-flight queue draining, commit lag warnings, and `append-entry` timing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/FollowerAppendLogEntryGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/LeaderAppendLogEntryGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/LeaderAppendLogEntryGenerator.java

## Purpose
Freon/Vapor generator that configures a standalone datanode as a Ratis leader and sends async Ozone write-chunk commands through `XceiverClientRatis`.

## Important APIs, types, and functions
Command `lalg`, options for pipeline id, chunk size, and next index. Extends `BaseAppendLogGenerator`. Uses `RaftClient` group management, `XceiverClientRatis`, `Pipeline`, `DatanodeDetails`, `ContainerCommandRequestProto`, `CreateContainerRequestProto`, `WriteChunkRequestProto`, `DatanodeBlockID`, in-flight queue, and metrics timer.

## Control flow
`call` initializes in-flight queue, config, random payload, server id, fake follower peer, plaintext Ratis stub, Freon state, and optionally configures a Ratis group. After a startup sleep, it creates a single-node Ratis pipeline, connects an xceiver client, creates container 1, then Freon operations send async write-chunk commands and remove in-flight IDs when futures complete.

## State and persistence behavior
Creates container and chunk data on the target datanode through normal xceiver/Ratis paths. Maintains in-flight step IDs but does not explicitly close the xceiver client in this source.

## Dependencies and integration points
Exercises datanode Ratis leader path, Xceiver client pipeline construction, Ozone container command protobufs, and Freon metrics.

## Risks and edge cases
Fake follower peers use duplicate IDs with different addresses. The `nextIndex` option only gates group configuration and is otherwise unused. Container id is hard-coded to 1, which can collide with existing state.

## Test signals
No direct tests. Runtime signals are create-container response, async future completions, in-flight queue behavior, and `append-entry` timer metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/LeaderAppendLogEntryGenerator.java -->
