# subset-b-008052 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestListInfoSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestListInfoSubcommand.java

Purpose: This JUnit suite verifies the SCM admin datanode `ListInfoSubcommand` output contract for text and JSON modes. It exercises listing all nodes, selecting a node by UUID, ordering by usage, volume counters, and filtering nodes that have failed volumes.

Important APIs and types: The test constructs protobuf `HddsProtos.Node` and `DatanodeUsageInfoProto` values, mocks `ScmClient.queryNode`, `ScmClient.getDatanodeUsageInfo`, and `ScmClient.listPipelines`, drives parsing with picocli `CommandLine`, and validates JSON through Jackson `ObjectMapper`.

Control flow: Each test configures a mock SCM response, parses CLI arguments into the same command instance, invokes `cmd.execute(scmClient)`, and inspects captured stdout/stderr. Helper methods build four nodes with varied health and operational states and validate JSON/text usage ordering.

State and persistence behavior: There is no persistent state. Runtime state is captured console output, mutable command options parsed by picocli, and generated UUID-backed protobuf fixtures.

Dependencies and integration points: The test anchors the CLI-to-`ScmClient` boundary and output fields consumed by operators and automation, including `--json`, `--id`, `--most-used`, `--least-used`, and `--nodes-with-failed-volumes`.

Risks: Several assertions depend on exact labels and ordering, so formatting changes can break tests even when data is correct. Reusing the command instance after parsing different flags relies on command option reset behavior.

Test signals: Signals include valid JSON arrays, expected node counts, presence and ordering of health states, mutual-exclusion exceptions, usage ratio sorting, volume count fields, failed volume paths, and rejection of failed-volume filtering with explicit node selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestListInfoSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestMaintenanceSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestMaintenanceSubCommand.java

Purpose: This suite validates the datanode maintenance CLI behavior when hostnames come from arguments or stdin and when SCM reports per-host administration errors.

Important APIs and types: It uses `MaintenanceSubCommand`, mocked `ScmClient`, `DatanodeAdminError`, picocli `CommandLine`, and captured `System.out`/`System.err`.

Control flow: Setup redirects console streams and creates a mock client. Tests parse either `"-"` for stdin or explicit hostnames, then call `cmd.execute(scmClient)`. Success paths expect a heading and listed hosts; the failure path stubs `startMaintenanceNodes` to return one `DatanodeAdminError` and expects `IOException`.

State and persistence behavior: No durable state is written. Input state may be `System.in`, and output state is captured byte buffers.

Dependencies and integration points: The command is integrated with `ScmClient.startMaintenanceNodes(List, int, boolean)`, stdin hostname parsing, and CLI user-facing error reporting.

Risks: The stdin test stubs `decommissionNodes` even though normal maintenance uses `startMaintenanceNodes`, so that path may not fully assert the current backend call. Exact regex output checks can be brittle to text revisions.

Test signals: Expected maintenance heading, host echoing, stderr line `Error: host1: host1 error`, and thrown `IOException` when SCM returns errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestMaintenanceSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestRecommissionSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestRecommissionSubCommand.java

Purpose: This test file verifies recommission CLI output and error propagation for datanode host lists passed directly or read from stdin.

Important APIs and types: It uses `RecommissionSubCommand`, mocked `ScmClient.recommissionNodes`, `DatanodeAdminError`, picocli, byte-array console capture, and regex-based assertions.

Control flow: Tests parse stdin marker `"-"` or host arguments, invoke the command, then assert that the command prints a recommission heading and each hostname. The error test returns a single admin error, expects `IOException`, and checks stderr for the formatted error.

State and persistence behavior: There is no on-disk state. Temporary state is limited to `System.in`, redirected `System.out`/`System.err`, and Mockito stubs.

Dependencies and integration points: The suite anchors the CLI user contract around `ScmClient.recommissionNodes(List)` and host ingestion from both terminal input styles.

Risks: Like the maintenance test, the stdin test stubs `decommissionNodes` instead of the recommission method, so it mostly verifies output parsing and not the backend invocation in that path.

Test signals: Recommission heading, exact host lines, stderr admin error formatting, and `IOException` on non-empty SCM error results.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestRecommissionSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestUsageInfoSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestUsageInfoSubcommand.java

Purpose: This suite verifies the standalone datanode usage report command in JSON and text modes.

Important APIs and types: It uses `UsageInfoSubcommand`, mocked `ScmClient.getDatanodeUsageInfo`, protobuf `DatanodeUsageInfoProto`, `MockDatanodeDetails`, Jackson `JsonNode`, AssertJ text assertions, and picocli.

Control flow: The fixture redirects output, stubs one usage record, parses `-m` with or without `--json`, executes the command, then checks JSON numeric fields or text labels.

State and persistence behavior: There is no persistence. The command consumes in-memory protobuf usage data and emits formatted report output.

Dependencies and integration points: The test protects the CLI mapping from SCM usage protobuf fields to operator-visible values: Ozone capacity, used, available, filesystem values, container count, and pipeline count.

Risks: Percentage calculations are validated for one simple fixture only. Text alignment assertions depend on label spacing and may require updates after formatting changes.

Test signals: JSON array node type, datanode details presence, exact capacity/usage values and percentages, and presence of every expected aligned text field.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestUsageInfoSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/pipeline/TestClosePipelinesSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/pipeline/TestClosePipelinesSubCommand.java

Purpose: This parameterized test validates `ClosePipelineSubcommand --all` filtering before issuing close operations.

Important APIs and types: It builds `Pipeline` instances with `StandaloneReplicationConfig`, `RatisReplicationConfig`, `ECReplicationConfig`, `PipelineID`, and synthetic `DatanodeDetails`, then mocks `ScmClient.listPipelines`.

Control flow: A method source supplies CLI flags and expected "Sending close command" counts. Setup creates the command, captures streams, and returns a mixed pipeline list. Each case parses flags, executes the command, and asserts exact stdout.

State and persistence behavior: No durable state is touched. Runtime state is a generated pipeline list with OPEN and CLOSED states.

Dependencies and integration points: The suite anchors close-all filter semantics across replication factor, replication type, EC config strings, and legacy factor flags.

Risks: The test verifies only the printed count, not that the expected pipeline IDs are closed or that `ScmClient.closePipeline` is called. Random IDs are irrelevant to assertions.

Test signals: Exact output counts for unfiltered, RATIS factor, EC replication/type, type-only, and closed-only cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/pipeline/TestClosePipelinesSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/pipeline/TestListPipelinesSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/pipeline/TestListPipelinesSubCommand.java

Purpose: This test suite verifies `ListPipelinesSubcommand` filtering by pipeline state, replication type, replication config, and legacy factor/state flags.

Important APIs and types: It uses Ozone replication config classes, `Pipeline`, `PipelineID`, `DatanodeDetails`, mocked `ScmClient.listPipelines`, and picocli parsing.

Control flow: Setup builds six pipelines across STANDALONE, RATIS, and EC replication with OPEN/CLOSED states. Each test parses specific options, executes the command, and checks output line counts or absence of unrelated state/type strings.

State and persistence behavior: No persistence is involved. Runtime state is generated pipeline metadata and captured stdout.

Dependencies and integration points: The test protects filter compatibility between modern `-r/-t/-s` flags and legacy `-ffc/-fst` flags.

Risks: Assertions mostly count lines and search substrings, so they can miss subtle formatting or wrong-ID issues. Exceptions are asserted at execute time rather than parse time for invalid combinations.

Test signals: All pipelines returned with no filter, OPEN-only exclusion of CLOSED, illegal replication without type, mutual exclusion of legacy and modern replication filters, EC config matching, and combined state/replication filters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/pipeline/TestListPipelinesSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/util/TestDurationUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/util/TestDurationUtil.java

Purpose: This compact parameterized suite locks down the formatting contract of `DurationUtil.getPrettyDuration`.

Important APIs and types: It uses Java `Duration`, JUnit parameterized tests, `Arguments`, and `DurationUtil`.

Control flow: Positive cases map durations from zero through days and `Long.MAX_VALUE` seconds to expected strings. Negative cases pass negative durations and expect `IllegalStateException`.

State and persistence behavior: There is no runtime state beyond immutable `Duration` objects and no persistence.

Dependencies and integration points: The utility output likely appears in CLI/admin reporting where stable hour/minute/second formatting matters.

Risks: The test covers second precision only and does not document fractional duration handling. The `Long.MAX_VALUE` case guards overflow-prone conversion.

Test signals: Exact strings such as `0s`, `1m 0s`, `24h 0m 0s`, and rejection of negative durations including `Long.MIN_VALUE` seconds.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/util/TestDurationUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/admin/om/snapshot/TestDefragSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/admin/om/snapshot/TestDefragSubCommand.java

Purpose: This suite verifies OM snapshot defragmentation CLI behavior for wait/no-wait execution and service/node targeting options.

Important APIs and types: It defines `TestableDefragSubCommand` to override `createClient`, uses mocked `OMAdminProtocolClientSideImpl`, `OzoneConfiguration`, `OMNodeDetails`, Mockito verification, and picocli.

Control flow: Setup injects the mock client and redirects output. Tests parse default or option-rich arguments, execute the command, verify `triggerSnapshotDefrag` is called with `false` for waiting or `true` for no-wait, and assert success/failure text.

State and persistence behavior: No persistent state is changed. The command would normally open an OM admin protocol client; the test replaces it with a mock and verifies close behavior is harmless.

Dependencies and integration points: It anchors the admin CLI contract to OM admin RPC for snapshot defrag service control.

Risks: The test calls `cmd.execute(omAdminClient)` directly despite the override being available, so connection construction and service-id/node-id resolution are not deeply exercised.

Test signals: Correct boolean passed to `triggerSnapshotDefrag`, success text, failure/interruption text, and background execution message under `--no-wait`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/admin/om/snapshot/TestDefragSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/scm/TestDecommissionScmSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/scm/TestDecommissionScmSubcommand.java

Purpose: This test validates SCM decommission CLI input requirements, success reporting, and backend error propagation.

Important APIs and types: It uses `DecommissionScmSubcommand`, `OzoneAdmin`, mocked `ScmClient.decommissionScm`, `DecommissionScmResponseProto`, `GenericTestUtils` output capturers, and picocli.

Control flow: The first test invokes top-level `ozone admin scm decommission` without `--nodeid` and expects usage text on stderr, then parses a UUID node ID and stubs a successful response. The second stubs a failure response and expects an `IOException` containing the server error.

State and persistence behavior: No persistence is involved. Runtime state is a UUID option value and captured console output.

Dependencies and integration points: The suite anchors the admin command to SCM decommission RPC response semantics.

Risks: Usage validation is exercised through `OzoneAdmin.execute`, while execution success is tested directly on the subcommand, leaving some full CLI wiring untested.

Test signals: Usage output for missing node ID, success output containing the selected SCM ID, and thrown `IOException` when SCM reports `success=false`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/scm/TestDecommissionScmSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/scm/TestGetScmRatisRolesSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/scm/TestGetScmRatisRolesSubcommand.java

Purpose: This unit test verifies table-formatted output for the SCM HA Ratis roles command.

Important APIs and types: It uses `GetScmRatisRolesSubcommand`, mocked `ScmClient.getScmRoles`, picocli, and `GenericTestUtils.SystemOutCapturer`.

Control flow: The test parses `--table`, stubs three colon-separated SCM role strings, executes the command, and checks formatted rows for hostname, port, role, and UUID alignment.

State and persistence behavior: There is no persistent state. The input state is a list of role strings returned by SCM.

Dependencies and integration points: The command depends on SCM role strings using `host:port:role:id:ip` layout and transforms them into operator-readable table output.

Risks: The parser contract for role strings is implicit; malformed entries are not covered. Assertions depend on spacing in the table formatter.

Test signals: Captured output contains all three formatted role rows, including LEADER and FOLLOWER alignment.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/scm/TestGetScmRatisRolesSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/scm/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/scm/package-info.java

Purpose: This package descriptor documents the test package as tooling around converting Ozone manager metadata to SQL DB, though the package contains SCM admin CLI tests in this subset.

Important APIs and types: It declares package `org.apache.hadoop.ozone.scm` and exports no runtime types.

Control flow: There is no executable control flow.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: Java tooling and Javadocs consume this metadata for package-level documentation.

Risks: The description appears stale or mismatched for the SCM test package, which can mislead readers and generated documentation.

Test signals: No direct test signal beyond successful compilation of the package declaration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/ozone/scm/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/dev-support/findbugsExcludeFile.xml

Purpose: This SpotBugs/FindBugs filter file is the module-local exclusion hook for `ozone-cli-debug`.

Important APIs and types: It contains a root `<FindBugsFilter>` element with no `<Match>` entries.

Control flow: There is no executable flow; build tooling reads the XML during static analysis.

State and persistence behavior: It persists static-analysis configuration only.

Dependencies and integration points: `cli-debug/pom.xml` points the SpotBugs Maven plugin at this file through `${basedir}/dev-support/findbugsExcludeFile.xml`.

Risks: An empty filter is low risk and means no module-specific warnings are suppressed. Future suppressions should be narrow because this module includes diagnostic tools that interact with local files, SQLite, RocksDB, and Kerberos state.

Test signals: Build/static-analysis behavior is the signal; there are no runtime tests in the file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/pom.xml

Purpose: This Maven module definition builds the `ozone-cli-debug` jar, a collection of developer/operator diagnostic commands for Ozone.

Important APIs and types: It declares artifact `org.apache.ozone:ozone-cli-debug:2.3.0-SNAPSHOT`, enables classpath generation, and depends on picocli, Jackson, Guava, Hadoop auth/common/HDFS, RocksDB JNI, SQLite JDBC, Ozone/Hdds modules, Recon, Ratis tools, JGraphT, and runtime logging/codec libraries.

Control flow: Maven resolves dependencies, runs the compiler with MetaInfServices and picocli Graal native-image annotation processors, and applies SpotBugs plus an enforcer rule overriding selected banned annotations/imports.

State and persistence behavior: The file persists build configuration and dependency graph. It does not define runtime state.

Dependencies and integration points: This module intentionally integrates with many Ozone internals: DB definitions, datanode container stores, OM/SCM metadata, Recon DBs, security auth, and CLI plugin discovery through `@MetaInfServices`.

Risks: The broad dependency set increases classpath conflict risk and makes the debug CLI sensitive to internal API changes. The explicit exclusion of Spring JDBC from Recon reduces transitive footprint. Annotation processor configuration is required for service metadata and native-image config generation.

Test signals: Maven compile/test/static-analysis success, generated service descriptors, and SpotBugs using the module exclude filter.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/CheckNative.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/CheckNative.java

Purpose: `CheckNative` implements `ozone debug checknative`, reporting whether Hadoop and Ozone native libraries are loaded.

Important APIs and types: It extends `AbstractSubcommand`, implements `Callable<Void>` and `DebugSubcommand`, and is registered via `@MetaInfServices`. It uses `NativeCodeLoader`, `ErasureCodeNative`, `OpensslCipher`, `ManagedRocksObjectUtils`, and `NativeLibraryLoader`.

Control flow: `call()` builds an ordered map of library names to formatted load results, loads RocksDB and rocks-tools libraries where possible, computes the widest label, and prints a compact table.

State and persistence behavior: It does not persist data. It may load native libraries into the JVM process, which is process-global state.

Dependencies and integration points: The command integrates with the extensible debug CLI and native library discovery for Hadoop, ISA-L, OpenSSL, RocksDB, and rocks-tools JNI.

Risks: Loading native libraries has side effects and can fail based on host packaging. OpenSSL reporting intentionally suppresses a cryptic failure reason when Hadoop native itself is not loaded.

Test signals: Useful signals are printed true/false statuses and library names or failure reasons; no dedicated test is in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/CheckNative.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/DBDefinitionFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/DBDefinitionFactory.java

Purpose: `DBDefinitionFactory` maps Ozone/RocksDB paths or names to the correct `DBDefinition` used by debug DB scanners.

Important APIs and types: It uses `DBDefinition`, `SCMDBDefinition`, `OMDBDefinition`, `ReconSCMDBDefinition`, `ReconDBDefinition`, datanode schema one/two/three DB definitions, `WitnessedContainerDBDefinition`, and an `AtomicReference` for datanode schema version.

Control flow: Static initialization registers known DB names. `getDefinition(String)` normalizes OM snapshot DB names to OM DB and falls back to Recon DB prefix handling. `getDefinition(Path, ConfigurationSource)` inspects the path filename and chooses a datanode DB definition when the name ends with the container DB suffix.

State and persistence behavior: The only mutable state is the process-wide selected datanode DB schema version set by `setDnDBSchemaVersion`. No files are written.

Dependencies and integration points: It is central to `DBScanner` and `ValueSchema`, bridging CLI options such as `--dn-schema` to Ozone metadata codecs.

Risks: The schema version is global mutable state, so concurrent scans in one JVM could interfere. Unknown DB names return null and require callers to emit user-facing errors.

Test signals: Expected signals are correct DB definition resolution for OM snapshots, Recon DB prefixes, SCM/OM DBs, witnessed containers, and datanode schema-specific container DB paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/DBDefinitionFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/OzoneDebug.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/OzoneDebug.java

Purpose: `OzoneDebug` is the top-level `ozone debug` shell entry point.

Important APIs and types: It extends `Shell`, implements `ExtensibleParentCommand`, uses `HddsVersionProvider`, and declares `DebugSubcommand` as the service-loaded subcommand type.

Control flow: `main` creates an instance and delegates to `run(argv)`. `subcommandType()` tells the parent command loader to discover implementations of `DebugSubcommand`.

State and persistence behavior: There is no persistent state. Runtime state is picocli command parsing and service discovery.

Dependencies and integration points: It is the integration point for all debug subcommands registered with `@MetaInfServices(DebugSubcommand.class)`, including native checks, ldb, audit parser, datanode, Kerberos, and log commands.

Risks: Subcommand discovery depends on generated service metadata and classpath correctness. The command name includes a space (`ozone debug`) plus alias `debug`, so launcher wiring must preserve intended invocation style.

Test signals: Successful help/version output and discovery of debug subcommands are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/OzoneDebug.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/RocksDBUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/RocksDBUtils.java

Purpose: `RocksDBUtils` provides shared helper methods for debug commands that inspect RocksDB stores.

Important APIs and types: It uses `RocksDatabase.listColumnFamiliesEmptyOptions`, RocksDB `ColumnFamilyDescriptor` and `ColumnFamilyHandle`, `ManagedRocksDB`, `Codec<T>`, and `StringCodec`.

Control flow: One method lists column-family descriptors from a DB path, another finds a handle by UTF-8 name bytes, and `getValue` performs a typed lookup using a string key codec and caller-provided value codec.

State and persistence behavior: It does not mutate DBs. Reads occur through a supplied RocksDB handle, generally opened read-only by callers.

Dependencies and integration points: The helpers support `Checkpoint`, `DBScanner`, and other ldb-style commands that need consistent column family enumeration and typed lookup.

Risks: `getColumnFamilyHandle` returns null when not found, so callers must handle that. `getValue` assumes string keys and is not appropriate for long/protobuf-keyed tables.

Test signals: Expected signals are correct descriptor enumeration, matching handles by name, null on missing column family, and decoded values for existing string keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/RocksDBUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/VersionDebug.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/VersionDebug.java

Purpose: `VersionDebug` prints local Ozone component version metadata as JSON without contacting services.

Important APIs and types: It implements `Callable<Void>` and `DebugSubcommand`, registers with `@MetaInfServices`, uses `ClientVersion`, `DatanodeVersion`, `OzoneManagerVersion`, `ComponentVersion`, `OzoneVersionInfo`, Guava `ImmutableSortedMap`, and `JsonUtils`.

Control flow: `call()` constructs a sorted nested map containing Ozone revision/url/version plus current component version names and protobuf values, then pretty-prints it to stdout.

State and persistence behavior: No state is modified or persisted. Output reflects constants in the loaded artifacts.

Dependencies and integration points: The command helps compare feature support across nodes and integrates into the debug CLI command registry.

Risks: It reports only the local classpath/artifact versions, not live cluster versions. If a component enum changes, `asMap` still serializes only the current constant.

Test signals: Valid JSON with `ozone` and `components` keys, and component version entries for client, datanode, and OM.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/VersionDebug.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/AuditParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/AuditParser.java

Purpose: `AuditParser` is the parent command for parsing Ozone audit logs into a SQLite database and querying them.

Important APIs and types: It implements `DebugSubcommand`, registers with `@MetaInfServices`, uses picocli `@Command`, `@Parameters`, `HddsVersionProvider`, and subcommands `LoadCommandHandler`, `TemplateCommandHandler`, and `QueryCommandHandler`.

Control flow: Picocli parses one required database path at the parent level, then dispatches to load/template/query handlers. `getDatabase()` exposes that path to child commands through `@ParentCommand`.

State and persistence behavior: The command itself holds only the parsed database path. SQLite persistence is performed by `DatabaseHelper` in the child command flows.

Dependencies and integration points: It integrates audit parsing into `ozone debug` and defines the table shape in user-facing parameter help.

Risks: The help describes a single `audit` table and uniqueness constraint; implementation correctness depends on external `commands.properties` SQL matching that description.

Test signals: CLI help, database parameter parsing, and successful dispatch to load/query/template handlers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/AuditParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/common/DatabaseHelper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/common/DatabaseHelper.java

Purpose: `DatabaseHelper` owns SQLite setup, audit log parsing, batch inserts, and query execution for the audit parser.

Important APIs and types: It uses JDBC `DriverManager`, `Connection`, `PreparedStatement`, `ResultSet`, `Properties`, `ParserConsts`, Apache `StringUtils`, and `AuditEntry`.

Control flow: Static initialization loads `commands.properties`. `setup` creates the audit table then calls `insertAudits`. Log parsing reads UTF-8 lines, treats date-prefixed lines as new audit records, appends non-date lines as exception text, splits pipe-delimited fields, builds `AuditEntry` objects, and inserts them in batches of 1000. Query and template methods delegate to `executeStatement`.

State and persistence behavior: It creates and mutates a SQLite database at the provided path. Static `properties` is process-global configuration loaded from resources.

Dependencies and integration points: It is called by load, query, and template handlers and depends on resource SQL keys such as `createAuditTable`, `insertAuditEntry`, and template names.

Risks: `appendException` on an `AuditEntry` with null exception can produce `"null\n..."`. Parsing assumes fixed pipe fields and operation formatting, so malformed audit lines can fail. Custom query execution accepts arbitrary SQL despite help saying read-only.

Test signals: Database file creation, row insertion counts, duplicate handling via SQL uniqueness, template validation, tab-separated query output, and proper handling of multiline exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/common/DatabaseHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/common/ParserConsts.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/common/ParserConsts.java

Purpose: `ParserConsts` centralizes constants for the audit parser SQLite and log parsing implementation.

Important APIs and types: It defines JDBC driver `org.sqlite.JDBC`, SQLite connection prefix, audit date regex, properties resource name, and SQL property keys.

Control flow: There is no dynamic flow besides class loading.

State and persistence behavior: Constants guide persistent SQLite connection creation and table SQL lookup; the class itself has no state.

Dependencies and integration points: `DatabaseHelper` uses all constants to load resources, detect new audit entries, and open SQLite connections.

Risks: `DATE_REGEX` accepts any line beginning with `yyyy-MM-dd`, so log formats that begin that way but are not audit entries could be misclassified.

Test signals: Correct constants are indirectly validated by audit parser load/query behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/common/ParserConsts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/common/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/common/package-info.java

Purpose: This package descriptor documents helper and constants classes for the Ozone audit parser.

Important APIs and types: It declares only package metadata.

Control flow: There is no executable control flow.

State and persistence behavior: There is no state.

Dependencies and integration points: Javadocs consume this package-level description.

Risks: The declared package is `org.apache.hadoop.ozone.audit.parser.common`, while the source path and Java classes use `org.apache.hadoop.ozone.debug.audit.parser.common`. That mismatch can break or misplace package documentation and may be a compile/package-info consistency issue.

Test signals: Build success is the only direct signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/common/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/LoadCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/LoadCommandHandler.java

Purpose: `LoadCommandHandler` implements `ozone debug auditparser <db> load <logs>`.

Important APIs and types: It implements `Callable<Void>`, uses picocli `@Command`, `@Parameters`, `@ParentCommand`, `AuditParser`, `DatabaseHelper`, and `HddsVersionProvider`.

Control flow: Picocli captures one log file path and parent database path. `call()` invokes `DatabaseHelper.setup(database, logs)` and prints success or failure text.

State and persistence behavior: It can create and populate a SQLite database via `DatabaseHelper`. The handler itself stores only parsed command parameters.

Dependencies and integration points: It is a child command of `AuditParser` and depends on `DatabaseHelper` for table creation, parsing, and insert behavior.

Risks: The parameter description says "file(s)" but the implementation accepts a single string and `DatabaseHelper` reads one path. Exceptions from setup propagate instead of being converted to user-friendly CLI failures.

Test signals: Successful load message and resulting rows in the SQLite audit table.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/LoadCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/QueryCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/QueryCommandHandler.java

Purpose: `QueryCommandHandler` executes a custom SQL query against an audit parser SQLite database.

Important APIs and types: It uses picocli command/parameter/parent annotations, `AuditParser`, `DatabaseHelper.executeCustomQuery`, and catches `SQLException`.

Control flow: `call()` passes the query string and parent database path to `DatabaseHelper`, prints returned rows to stdout, and prints SQL errors to stderr.

State and persistence behavior: The handler normally reads from SQLite but does not enforce read-only SQL, so supplied statements could mutate state if JDBC allows them through `executeQuery` semantics.

Dependencies and integration points: It is a child command under `AuditParser` and exposes the raw database to operator-provided SQL.

Risks: Arbitrary SQL is accepted; validation is limited to JDBC exceptions. The description tells users to enclose the query in double quotes, which is shell-dependent.

Test signals: Expected output is tab-separated result rows or a printed SQL error message.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/QueryCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/TemplateCommandHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/TemplateCommandHandler.java

Purpose: `TemplateCommandHandler` executes named predefined audit queries.

Important APIs and types: It uses picocli annotations, `AuditParser`, `DatabaseHelper.validateTemplate`, `DatabaseHelper.executeTemplate`, and catches `SQLException`.

Control flow: `call()` validates the supplied template name against loaded SQL properties. Valid templates execute and print rows; invalid names print an error to stderr.

State and persistence behavior: The command reads from the SQLite audit DB and does not directly persist state.

Dependencies and integration points: It exposes templates documented in the command description, including top users, commands, and active times, backed by entries in `commands.properties`.

Risks: Template availability and help text can drift because available names are hard-coded in the description but validated dynamically from properties.

Test signals: Valid template output, invalid template error text, and SQL exception text on query failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/TemplateCommandHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/package-info.java

Purpose: This descriptor documents the audit parser command handler package.

Important APIs and types: It contains only package-level Javadoc.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: It is intended for generated Javadocs.

Risks: The declared package omits `.debug` (`org.apache.hadoop.ozone.audit.parser.handler`) while neighboring handler classes are in `org.apache.hadoop.ozone.debug.audit.parser.handler`.

Test signals: Compilation/package-info processing is the only signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/handler/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/model/AuditEntry.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/model/AuditEntry.java

Purpose: `AuditEntry` is the data model for parsed audit log records before insertion into SQLite.

Important APIs and types: It is a mutable POJO with fields for timestamp, level, logger, user, IP, operation, params, result, and exception, plus a nested fluent `Builder`.

Control flow: Callers either use setters or the builder to populate fields. `setException` trims text, and `appendException` appends a newline and trimmed continuation text to the existing exception string.

State and persistence behavior: Instances hold in-memory parsed state. `DatabaseHelper` maps instances into the persistent SQLite audit table.

Dependencies and integration points: The class is used by the audit parser's log parsing and insert path.

Risks: `appendException` assumes `exception` is already initialized; if it is null, concatenation can persist a `"null"` prefix. The builder does no validation, so malformed/null fields reach SQL binding.

Test signals: Expected signals are correct field extraction, multiline exception preservation, and inserted SQL column values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/model/AuditEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/model/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/model/package-info.java

Purpose: This descriptor documents the audit parser model package.

Important APIs and types: It exports no runtime type beyond package metadata.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: It is used by Javadoc tooling.

Risks: The package declaration is `org.apache.hadoop.ozone.audit.parser.model`, while `AuditEntry` uses `org.apache.hadoop.ozone.debug.audit.parser.model`, creating a package-info mismatch.

Test signals: Build/package-info processing only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/model/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/package-info.java

Purpose: This package descriptor documents the audit parser package.

Important APIs and types: It contains package-level Javadoc only.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Javadocs consume it for package documentation.

Risks: It declares `org.apache.hadoop.ozone.audit.parser` instead of `org.apache.hadoop.ozone.debug.audit.parser`, inconsistent with the source path and `AuditParser` class package.

Test signals: Compilation/package-info validation is the direct signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/DatanodeDebug.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/DatanodeDebug.java

Purpose: `DatanodeDebug` is the parent command for datanode-specific debug operations.

Important APIs and types: It implements `DebugSubcommand`, registers with `@MetaInfServices`, and declares `ContainerCommands` as its subcommand.

Control flow: Picocli dispatches `ozone debug datanode container ...` commands through this parent. The class itself contains no methods.

State and persistence behavior: No state is stored or persisted.

Dependencies and integration points: It integrates datanode local container inspection/export commands into the extensible debug CLI.

Risks: Service registration and subcommand class availability are required for discovery.

Test signals: CLI help/discovery showing `datanode` and `container` subcommands.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/DatanodeDebug.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/ContainerCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/ContainerCommands.java

Purpose: `ContainerCommands` groups datanode-local container replica debug commands and builds a read-only container view from configured storage volumes.

Important APIs and types: It extends `AbstractSubcommand`, uses `OzoneConfiguration`, `MutableVolumeSet`, `ContainerSet`, `ContainerController`, `ContainerReader`, `Handler`, `HddsVolume`, `DatanodeVersionFile`, `StorageVolumeUtil`, `HddsVolumeUtil`, `ContainerChecksumTreeManager`, and `JsonUtils`.

Control flow: `loadContainersFromVolumes` validates configured storage directories, creates a read-only `ContainerSet`, reads datanode UUID and cluster ID from storage metadata, creates volume sets and handlers, optionally loads schema-v3 DB stores read-only, then runs `ContainerReader` over each HDDS volume. Subcommands consume `getController()` and `getVolumeSet()`.

State and persistence behavior: It reads datanode VERSION files, storage directories, container metadata, and possibly RocksDB stores. Runtime state is the loaded `volumeSet` and `controller`; no mutation is intended.

Dependencies and integration points: It is the parent for list/info/export/inspect and reuses datanode container service internals outside a running datanode.

Risks: It assumes at least one configured storage directory and at least one cluster ID directory under `hdds`. Missing directories produce `IOException`; `findFirst().get()` can throw if no cluster dir exists.

Test signals: Successful container loading, JSON output from `outputContainer`, and clear errors for missing storage directories.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/ContainerCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/ExportSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/ExportSubcommand.java

Purpose: `ExportSubcommand` exports one or more local container replicas to tar files.

Important APIs and types: It implements `Callable<Void>`, uses parent `ContainerCommands`, `OnDemandContainerReplicationSource`, `ContainerReplicationSource`, `StorageContainerException`, and `CopyContainerCompression.NO_COMPRESSION`.

Control flow: The command loads containers from volumes, creates a replication source from the parent controller, then loops from the requested container ID for `--count` containers. It prepares each container, opens `container-<id>.tar` under `--dest`, copies data, ignores `CONTAINER_NOT_FOUND`, logs success, and increments the ID.

State and persistence behavior: It reads local container metadata/chunks and writes tar files to the destination directory. It does not mutate container stores.

Dependencies and integration points: It reuses the same replication source used by datanode replication paths, making exports faithful to transfer format.

Risks: Destination existence/writability is not prevalidated. If `CONTAINER_NOT_FOUND` occurs after the output file is created, an empty tar path may be left behind.

Test signals: Created tar files, log messages, and successful continuation over missing container IDs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/ExportSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/InfoSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/InfoSubcommand.java

Purpose: `InfoSubcommand` prints JSON metadata for one local container replica.

Important APIs and types: It uses parent `ContainerCommands`, `ContainerController.getContainer`, `Container`, and `ContainerCommands.outputContainer`.

Control flow: The command requires `--container`, loads containers from datanode volumes, looks up the container ID in the controller, and pretty-prints `ContainerData` if found.

State and persistence behavior: It reads local datanode container metadata and emits JSON. No writes occur.

Dependencies and integration points: It depends on the parent loading path and container service metadata model.

Risks: Missing containers produce no output and no error, which can be ambiguous for users and automation.

Test signals: JSON output for existing container data and quiet completion for absent IDs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/InfoSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/InspectSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/InspectSubcommand.java

Purpose: `InspectSubcommand` runs key-value container metadata inspection across all local replicas.

Important APIs and types: It extends `AbstractSubcommand`, uses parent `ContainerCommands`, `KeyValueContainerMetadataInspector`, `KeyValueContainerData`, `BlockUtils.getUncachedDatanodeStore`, and `DatanodeStore`.

Control flow: The command gets Ozone configuration, loads containers, creates an inspector in `INSPECT` mode, iterates all containers, skips non-key-value data, opens each container store read-only, processes metadata, and prints JSON. Per-container `IOException` is caught and printed to stderr with stack trace.

State and persistence behavior: It reads RocksDB/container metadata stores using uncached read-only handles. No mutation is intended.

Dependencies and integration points: It integrates datanode debug loading with the container metadata inspector used to validate key-value container DB consistency.

Risks: The command continues after individual failures, which is useful but can mix JSON stdout with stack traces on stderr. It assumes container data can be cast for key-value containers only.

Test signals: Inspector JSON per key-value container and explicit stderr failures for unreadable stores.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/InspectSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/ListSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/ListSubcommand.java

Purpose: `ListSubcommand` prints JSON metadata for every local container replica on the datanode.

Important APIs and types: It uses parent `ContainerCommands`, iterates `parent.getController().getContainers()`, and delegates serialization to `outputContainer`.

Control flow: `call()` loads containers from volumes and writes one pretty JSON object per container.

State and persistence behavior: It reads local container metadata and writes to stdout only.

Dependencies and integration points: It depends fully on `ContainerCommands.loadContainersFromVolumes` to construct the controller view.

Risks: Output is a stream of separate JSON objects rather than a single JSON array, which matters for automation. Large datanodes can produce substantial output.

Test signals: One serialized `ContainerData` object per loaded container.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/ListSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/package-info.java

Purpose: This descriptor documents datanode container replica debug commands.

Important APIs and types: It declares package `org.apache.hadoop.ozone.debug.datanode.container`.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Javadocs and package tooling consume the description.

Risks: Low; package declaration matches the source path.

Test signals: Compilation/package-info processing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/container/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/package-info.java

Purpose: This descriptor documents the datanode debug command package.

Important APIs and types: It declares package `org.apache.hadoop.ozone.debug.datanode`.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Used by generated documentation.

Risks: Low; package declaration is path-aligned.

Test signals: Build/package-info processing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/datanode/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/AuthorizationProbe.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/AuthorizationProbe.java

Purpose: `AuthorizationProbe` diagnoses Ozone and Hadoop authorization configuration after basic Kerberos/security checks.

Important APIs and types: It extends `ConfigProbe`, returns `ProbeResult`, and reads config keys from `OzoneConfigKeys`, `CommonConfigurationKeysPublic`, `OMConfigKeys`, and `HddsConfigKeys`.

Control flow: The probe prints relevant security, authorization, ACL, and protocol ACL config values. It returns WARN when Ozone security is disabled, Ozone authorization is disabled, Hadoop service authorization is disabled, or Ozone ACL enforcement is disabled while authorization is otherwise enabled.

State and persistence behavior: It only reads `OzoneConfiguration` and writes diagnostics to stdout/stderr.

Dependencies and integration points: It runs within `DiagnoseSubcommand` and contributes to the aggregate PASS/WARN/FAIL summary.

Risks: Disabled security is treated as WARN rather than FAIL, appropriate for diagnostics but not enforcement. It prints values but does not validate ACL syntax.

Test signals: Printed config values and WARN/PASS classification for secure and non-secure configurations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/AuthorizationProbe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/ConfigProbe.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/ConfigProbe.java

Purpose: `ConfigProbe` is the base class for Kerberos diagnostic probes, providing printing, warning/error, file-read validation, and krb5.conf resolution helpers.

Important APIs and types: It implements `DiagnosticProbe` indirectly, uses `OzoneConfiguration`, `File`, `Files.newInputStream`, and environment/system properties.

Control flow: `printValue` formats key/value lines, with special handling for auth-to-local output. `print` reads trimmed config values. `canReadFile` checks null, existence, regular file, readability, and non-empty content. `getKrb5ConfigFile` prefers JVM property, then `KRB5_CONFIG`, then `/etc/krb5.conf`.

State and persistence behavior: No persistence. It reads local filesystem metadata and environment/JVM state.

Dependencies and integration points: All Kerberos probes inherit these helpers, so output format and file validation behavior are centralized.

Risks: `File.canRead` plus opening catches most cases, but permissions can vary under different users. Special formatting tied to strings starting with `to Local user` is presentation-specific.

Test signals: Consistent WARNING/ERROR prefixes, correct krb5.conf precedence, and non-empty file validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/ConfigProbe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/DiagnoseSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/DiagnoseSubcommand.java

Purpose: `DiagnoseSubcommand` runs the ordered Kerberos diagnostic suite and summarizes PASS/WARN/FAIL counts.

Important APIs and types: It extends `AbstractSubcommand`, implements `Callable<Integer>`, uses `OzoneConfiguration`, `DiagnosticProbe`, `ProbeResult`, and concrete probe classes.

Control flow: `call()` prints a header, builds a fixed probe list, and executes each probe serially. During each probe it temporarily redirects `System.out` and `System.err` into a UTF-8 buffer, restores streams, prints probe output through command output, increments result counters, and returns exit code 1 if any probe fails.

State and persistence behavior: It reads configuration, environment, filesystem, and JVM state through probes. It mutates global system streams temporarily and restores them in `finally`.

Dependencies and integration points: It is a subcommand of `KerberosSubcommand` and coordinates all probe contracts.

Risks: Temporarily redirecting global streams is process-wide and unsafe under concurrent command execution. Catching `Throwable` keeps diagnostics robust but may mask serious errors as probe failures.

Test signals: Probe headers, per-probe status lines, summary counts, and return code 1 when failures are present.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/DiagnoseSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/DiagnosticProbe.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/DiagnosticProbe.java

Purpose: `DiagnosticProbe` defines the contract for Kerberos diagnostic checks.

Important APIs and types: It declares `name()` and `test(OzoneConfiguration)` returning `ProbeResult`.

Control flow: Implementations are invoked by `DiagnoseSubcommand` in fixed order.

State and persistence behavior: The interface itself has no state. Implementations may read config, environment, filesystem, or JVM state.

Dependencies and integration points: This abstraction allows new probes to be added to the diagnose flow with consistent naming and result classification.

Risks: No severity detail beyond PASS/WARN/FAIL is available, so richer diagnostics must be printed as text.

Test signals: Probe implementations satisfy the interface and return meaningful `ProbeResult` values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/DiagnosticProbe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/EnvironmentProbe.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/EnvironmentProbe.java

Purpose: `EnvironmentProbe` prints environment variables relevant to Kerberos and Ozone configuration discovery.

Important APIs and types: It extends `ConfigProbe` and reads process environment through `System.getenv`.

Control flow: `test()` prints `KRB5_CONFIG`, `KRB5CCNAME`, `OZONE_CONF_DIR`, `HADOOP_CONF_DIR`, and `JAVA_SECURITY_KRB5_CONF`, then returns PASS.

State and persistence behavior: It reads environment variables only and does not persist or mutate state.

Dependencies and integration points: It supplies context early in `DiagnoseSubcommand` for later file/config failures.

Risks: It does not validate whether paths exist or whether `JAVA_SECURITY_KRB5_CONF` maps to an actual JVM property; it is informational.

Test signals: Output lines for all expected environment variable names and PASS result.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/EnvironmentProbe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/HostProbe.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/HostProbe.java

Purpose: `HostProbe` reports basic host, user, and Java runtime information for Kerberos troubleshooting.

Important APIs and types: It extends `ConfigProbe`, uses `InetAddress.getLocalHost().getCanonicalHostName`, and JVM system properties.

Control flow: It attempts hostname resolution, user-name lookup, and Java-version lookup independently. Hostname or user failures mark FAIL; Java-version failure can downgrade PASS to WARN.

State and persistence behavior: It reads host/JVM state only.

Dependencies and integration points: It is the first probe in `DiagnoseSubcommand`, establishing local process context.

Risks: Hostname resolution can block or fail based on DNS/hosts configuration; this is intentionally surfaced as FAIL.

Test signals: Printed hostname, user, Java version, and correct PASS/WARN/FAIL classification under simulated failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/HostProbe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/HttpAuthProbe.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/HttpAuthProbe.java

Purpose: `HttpAuthProbe` prints HTTP authentication settings for Ozone web endpoints.

Important APIs and types: It extends `ConfigProbe` and reads OM, SCM, datanode, Recon, and S3 Gateway HTTP auth config keys.

Control flow: `test()` prints each key and always returns PASS.

State and persistence behavior: It reads `OzoneConfiguration` only.

Dependencies and integration points: It is part of the Kerberos diagnose flow and helps identify whether WebUI/REST endpoints are configured for Kerberos.

Risks: It does not enforce validation and directly references the S3G key string to avoid a cyclic dependency, so key renames could drift.

Test signals: Printed auth type values for all five services and PASS result.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/HttpAuthProbe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/JvmKerberosProbe.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/JvmKerberosProbe.java

Purpose: `JvmKerberosProbe` validates JVM-level Kerberos system properties and effective krb5.conf readability.

Important APIs and types: It extends `ConfigProbe`, reads JVM properties `java.security.krb5.conf`, `java.security.krb5.realm`, `java.security.krb5.kdc`, and `sun.security.krb5.debug`.

Control flow: It prints all relevant properties, defaults missing krb5.conf to `/etc/krb5.conf`, validates file readability, warns on partial realm/KDC configuration, warns when explicit realm/KDC and krb5.conf are both set, and reports debug mode if enabled.

State and persistence behavior: It reads JVM properties and filesystem state only.

Dependencies and integration points: It runs before system Kerberos config and principal mapping probes in `DiagnoseSubcommand`.

Risks: Defaulting to `/etc/krb5.conf` differs from `ConfigProbe.getKrb5ConfigFile`, which also considers `KRB5_CONFIG`; that distinction can produce different diagnostics.

Test signals: FAIL on unreadable krb5.conf, WARN for partial/conflicting config, and PASS for readable consistent settings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/JvmKerberosProbe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KerberosConfigProbe.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KerberosConfigProbe.java

Purpose: `KerberosConfigProbe` validates system-level krb5.conf availability and default realm resolution.

Important APIs and types: It extends `ConfigProbe`, reads `KRB5_CONFIG`, uses `KerberosUtil.getDefaultRealm`, and validates a `File`.

Control flow: The probe chooses `KRB5_CONFIG` or `/etc/krb5.conf`, prints the path, checks that it is readable and non-empty, then prints the default realm or returns FAIL on resolution errors.

State and persistence behavior: It reads environment, filesystem, and Kerberos library state only.

Dependencies and integration points: It provides foundational Kerberos config validation for the diagnosis sequence.

Risks: It ignores the JVM `java.security.krb5.conf` property, unlike `ConfigProbe.getKrb5ConfigFile`, so results may differ from JVM probe behavior.

Test signals: PASS with readable config and resolvable default realm; FAIL for missing/unreadable file or realm lookup failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KerberosConfigProbe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KerberosSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KerberosSubcommand.java

Purpose: `KerberosSubcommand` groups Kerberos debug commands under `ozone debug kerberos`.

Important APIs and types: It implements `DebugSubcommand`, registers with `@MetaInfServices`, and declares `DiagnoseSubcommand` and `TranslatePrincipalSubcommand`.

Control flow: Picocli routes nested commands through this parent; the class contains no executable method.

State and persistence behavior: No state or persistence.

Dependencies and integration points: It integrates Kerberos diagnostics and principal translation into the extensible debug command tree.

Risks: Discovery depends on service metadata generated at compile time.

Test signals: Help/discovery for `diagnose` and `translate-principal` subcommands.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KerberosSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KerberosTicketProbe.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KerberosTicketProbe.java

Purpose: `KerberosTicketProbe` checks whether Hadoop is configured for Kerberos and whether the current process has active Kerberos credentials.

Important APIs and types: It extends `ConfigProbe`, uses `UserGroupInformation`, `CommonConfigurationKeysPublic.HADOOP_SECURITY_AUTHENTICATION`, and `KRB5CCNAME`.

Control flow: The probe sets UGI configuration, checks whether authentication is `kerberos`, warns if not, reads the login user and auth method, checks `hasKerberosCredentials`, prints ticket cache information, and returns WARN for inactive/missing credentials or PASS for a valid Kerberos login.

State and persistence behavior: It mutates process-global UGI configuration and reads current login/ticket state; no files are written.

Dependencies and integration points: It is part of the diagnostic suite and interacts with Hadoop security runtime state.

Risks: `UserGroupInformation.setConfiguration` is global and can affect later security checks in the same JVM. Ticket cache visibility depends on process environment.

Test signals: WARN for simple auth, WARN for Kerberos config without active ticket, PASS for valid Kerberos credentials, FAIL on UGI exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KerberosTicketProbe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KeytabProbe.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KeytabProbe.java

Purpose: `KeytabProbe` validates configured service keytab files for Ozone components.

Important APIs and types: It extends `ConfigProbe`, reads keys from `OMConfigKeys`, `ScmConfig`, `HddsConfigKeys`, `ReconConfig`, and direct S3G config strings.

Control flow: The probe first checks Ozone security enabled. If disabled it returns WARN. Otherwise it iterates known keytab config keys; empty/unset paths are acceptable, but configured missing/unreadable/empty files mark FAIL. Valid files print `Keytab OK`.

State and persistence behavior: It reads configuration and filesystem state only.

Dependencies and integration points: It runs in the Kerberos diagnostic suite and covers OM, SCM, datanode, Recon, and S3G keytabs.

Risks: Security-enabled detection uses `Boolean.parseBoolean(conf.getTrimmed(...))` without the default helper, so unset config is treated as false. It does not inspect keytab contents beyond non-empty readability.

Test signals: WARN when security disabled, PASS when all configured keytabs are readable, FAIL when any configured keytab is missing or invalid.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KeytabProbe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KinitProbe.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KinitProbe.java

Purpose: `KinitProbe` verifies that the `kinit` executable is available and executable on `PATH`.

Important APIs and types: It extends `ConfigProbe`, uses `System.getenv("PATH")`, `File.exists`, and `File.canExecute`.

Control flow: The probe prints PATH, returns FAIL if PATH is unset, scans each colon-separated directory for `kinit`, returns FAIL if found but not executable, PASS if executable, and FAIL if not found.

State and persistence behavior: It reads environment and filesystem metadata only.

Dependencies and integration points: It helps distinguish ticket/config problems from a missing Kerberos client utility during diagnostics.

Risks: The path separator is hard-coded as `:`, matching Unix-like deployments but not Windows. It does not run `kinit`, only checks existence/executability.

Test signals: PASS with executable `kinit`, FAIL for unset PATH, non-executable found file, or missing executable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/KinitProbe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/PrincipalMappingProbe.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/PrincipalMappingProbe.java

Purpose: `PrincipalMappingProbe` validates Hadoop auth-to-local rules against configured Ozone service principals.

Important APIs and types: It extends `ConfigProbe`, uses `KerberosName`, `CommonConfigurationKeysPublic.HADOOP_SECURITY_AUTH_TO_LOCAL`, and service principal config keys for OM, SCM, datanode, Recon, and S3G.

Control flow: The probe first validates the effective krb5.conf file, prints auth-to-local rules, installs them with `KerberosName.setRules`, gathers configured principals, and attempts to translate each to a local short name. Missing principals return WARN; individual mapping failures downgrade to WARN.

State and persistence behavior: It reads configuration and filesystem state and mutates global `KerberosName` rules.

Dependencies and integration points: It is part of Kerberos diagnosis and complements `TranslatePrincipalSubcommand`.

Risks: Global KerberosName rule mutation can affect later code in the JVM. Principal strings containing `_HOST` may not map as expected without substitution.

Test signals: Printed principal-to-local mappings, WARN for no principals or per-principal failures, FAIL for unreadable krb5.conf.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/PrincipalMappingProbe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/ProbeResult.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/ProbeResult.java

Purpose: `ProbeResult` is the three-state severity enum for Kerberos diagnostic probes.

Important APIs and types: It defines `PASS`, `WARN`, and `FAIL`.

Control flow: `DiagnoseSubcommand` switches on this enum to print status lines, count summary values, and choose exit code.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Every `DiagnosticProbe` returns this enum.

Risks: The model has no field for remediation, machine-readable details, or skipped/not-applicable states; those must be expressed in text.

Test signals: Exhaustive switch behavior in diagnose and stable enum names in output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/ProbeResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/SecurityConfigProbe.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/SecurityConfigProbe.java

Purpose: `SecurityConfigProbe` prints and validates high-level Hadoop/Ozone security settings.

Important APIs and types: It extends `ConfigProbe`, reads Hadoop authentication/RPC protection/SASL resolver settings plus Ozone security, HTTP security, admin, token, and TLS keys.

Control flow: The probe prints all relevant keys, then warns if Hadoop auth is not Kerberos or Ozone security is not enabled. It returns PASS only when both primary settings are enabled.

State and persistence behavior: It reads `OzoneConfiguration` only.

Dependencies and integration points: It runs before authorization and HTTP auth probes in the Kerberos diagnostic flow.

Risks: It treats all non-Kerberos auth values as WARN, not FAIL. The warning for Ozone security prints `false` literally rather than the actual config string.

Test signals: Config printout and WARN/PASS classification based on auth and Ozone security booleans.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/SecurityConfigProbe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/TranslatePrincipalSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/TranslatePrincipalSubcommand.java

Purpose: `TranslatePrincipalSubcommand` translates supplied Kerberos principals to local users using configured auth-to-local rules.

Important APIs and types: It extends `AbstractSubcommand`, implements `Callable<Integer>`, accepts one or more picocli parameters, and uses `KerberosName`.

Control flow: The command prints a header, reads `hadoop.security.auth_to_local` from Ozone config with default `DEFAULT`, installs the rules globally, then loops over principals. Each successful translation prints a PASS block; failures print an error to stderr and a FAIL block. Exit code is 1 if any principal fails.

State and persistence behavior: It reads configuration and mutates global KerberosName rules. No files are written.

Dependencies and integration points: It is a child of `KerberosSubcommand` and provides an operator-facing focused variant of `PrincipalMappingProbe`.

Risks: Global rule mutation can leak within a long-lived JVM. It does not validate krb5.conf readability before constructing `KerberosName`.

Test signals: Printed short names, PASS/FAIL counts, and non-zero return code when translation fails.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/TranslatePrincipalSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/package-info.java

Purpose: This package descriptor documents Kerberos debug subcommands and probes.

Important APIs and types: It declares package `org.apache.hadoop.ozone.debug.kerberos`.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Used by package Javadocs.

Risks: Low; declaration matches source path.

Test signals: Build/package-info processing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/Checkpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/Checkpoint.java

Purpose: `Checkpoint` creates a RocksDB checkpoint from the database selected by the parent ldb command.

Important APIs and types: It extends `AbstractSubcommand`, implements `Callable<Void>`, uses parent `RDBParser`, `RocksDBUtils`, `ManagedRocksDB.openReadOnly`, and `ManagedCheckpoint`.

Control flow: The command lists column family descriptors, opens the DB read-only with handles, creates a managed checkpoint, writes it to `--output`, and prints the output path.

State and persistence behavior: It reads the source RocksDB and writes a checkpoint directory. It does not mutate the source DB.

Dependencies and integration points: It is a subcommand of `ozone debug ldb` and depends on RocksDB checkpoint APIs.

Risks: Output path validation and overwrite semantics are delegated to RocksDB. Column family handles are not explicitly closed in this file, relying on managed DB cleanup.

Test signals: Created checkpoint directory and success message.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/Checkpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/DBScanner.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/DBScanner.java

Purpose: `DBScanner` implements `ozone debug ldb scan`, decoding and printing rows from Ozone RocksDB column families with filtering, projection, count, range, batching, and output-file support.

Important APIs and types: It extends `AbstractSubcommand`, uses parent `RDBParser`, `DBDefinitionFactory`, `DBColumnFamilyDefinition`, `ManagedRocksDB`, `ManagedRocksIterator`, `ManagedReadOptions`, `ManagedSlice`, Ozone codecs for string/long/container/pipeline keys, `DatanodeSchemaThreeDBDefinition`, Jackson `ObjectMapper/ObjectWriter`, `Filter`, Java reflection `Field`, and a threaded `LogWriter`.

Control flow: `call()` opens the selected RocksDB read-only and delegates to `printTable`. `printTable` validates limits, resolves the DB definition/table, handles `--show-count`, creates an iterator, and applies schema-v3 container bounds when `--container-id` is set. `processRecords` seeks to `--startkey`, converts and filters values, batches key/value bytes, submits parsing tasks, observes limits/end key, and waits for futures. `Task` decodes keys/values, optionally projects nested fields, serializes JSON, and sends sequenced chunks to `LogWriter`, which preserves iterator order despite concurrent parsing.

State and persistence behavior: It reads RocksDB only unless `--out` is used, in which case it writes JSON output files and may suffix files by `--max-records-per-file`. Runtime state includes global count, file suffix, a static `compact` option, and a static volatile exception flag.

Dependencies and integration points: It is the main consumer of Ozone DB definitions and codecs for OM, SCM, Recon, and datanode DBs. It integrates schema-v3 container key prefix logic with debug output formatting.

Risks: Reflection-based filters/projections can break on private field renames and set fields accessible. The static `compact` and `exception` flags are process-wide. Output JSON formatting relies on comma insertion across batches; error paths can still print closing delimiters. File output assumes parentFile is non-null, so a bare filename may risk null handling.

Test signals: Decoded JSON for table rows, count output, start/end key behavior for supported key types, schema-v3 key rendering, field filtering/projection, valid output ordering under multiple threads, and non-zero exit behavior when DB/table/filter errors occur.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/DBScanner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/ListTables.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/ListTables.java

Purpose: `ListTables` lists RocksDB column families for the parent ldb database path.

Important APIs and types: It implements `Callable<Void>`, uses parent `RDBParser`, `RocksDatabase.listColumnFamiliesEmptyOptions`, and UTF-8 decoding.

Control flow: `call()` obtains the DB path from the parent, lists column family byte names, converts each to a UTF-8 string, and prints one per line.

State and persistence behavior: It reads RocksDB metadata only and writes to stdout.

Dependencies and integration points: It is an ldb subcommand useful before `scan` or `value-schema`.

Risks: It assumes column family names are UTF-8, which matches Ozone table names.

Test signals: Printed column family list for a valid DB path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/ListTables.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/RDBParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/RDBParser.java

Purpose: `RDBParser` is the parent command for RocksDB inspection utilities under `ozone debug ldb`.

Important APIs and types: It implements `DebugSubcommand`, registers with `@MetaInfServices`, and declares `DBScanner`, `ListTables`, `ValueSchema`, and `Checkpoint` as subcommands.

Control flow: Picocli parses inherited required `--db` and dispatches to child commands, which access it via `getDbPath`.

State and persistence behavior: It stores the selected DB path in memory only.

Dependencies and integration points: It integrates RocksDB scanning, schema introspection, column-family listing, and checkpoint creation into the debug CLI.

Risks: All child commands require a valid local RocksDB path; no validation occurs at the parent setter.

Test signals: CLI help, inherited `--db` parsing, and child command access to the path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/RDBParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/ValueSchema.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/ValueSchema.java

Purpose: `ValueSchema` prints a JSON description of the Java value type stored in a selected RocksDB column family.

Important APIs and types: It extends `AbstractSubcommand`, uses `DBDefinitionFactory`, `DBColumnFamilyDefinition`, `JsonUtils`, reflection `Field`, `ParameterizedType`, collection handling, and `OzoneConfiguration`.

Control flow: `call()` validates `--depth` in `[0,10]`, resolves the DB definition from parent `--db` and `--dn-schema`, resolves the column family, recursively walks non-static fields of the value class up to the requested depth, and prints a JSON map keyed by value type name.

State and persistence behavior: It reads no DB rows and writes no persistent state. It updates `DBDefinitionFactory`'s process-wide datanode schema version.

Dependencies and integration points: It complements `DBScanner` by showing users available field paths for projection/filtering.

Risks: Interface/abstract fields produce empty structures, collection generic types may not be simple classes, and reflection exposes private implementation fields that can change without serialized schema changes.

Test signals: Error for invalid depth, incorrect DB path, or missing table; JSON field tree for supported table values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/ValueSchema.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/package-info.java

Purpose: This descriptor documents RocksDB debug commands.

Important APIs and types: It declares package `org.apache.hadoop.ozone.debug.ldb`.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Used by generated Javadocs.

Risks: Low; declaration matches source path.

Test signals: Build/package-info processing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/ldb/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/LogParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/LogParser.java

Purpose: `LogParser` is the parent debug command for log parsing and analysis.

Important APIs and types: It implements `DebugSubcommand`, registers with `@MetaInfServices`, and exposes `ContainerLogController`.

Control flow: Picocli routes `ozone debug log container ...` through this parent. The class itself has no executable methods.

State and persistence behavior: No state is stored in this parent.

Dependencies and integration points: It integrates container log analysis commands into the debug CLI.

Risks: The description notes logs must be extracted first; validation happens in subcommands, not here.

Test signals: CLI discovery and help output for the `log` command.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/LogParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ContainerInfoCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ContainerInfoCommand.java

Purpose: `ContainerInfoCommand` prints state-transition history and analysis for one container from the parsed container-log SQLite database.

Important APIs and types: It extends `AbstractSubcommand`, uses a positional `Long containerId`, parent `ContainerLogController`, and `ContainerDatanodeDatabase.showContainerDetails`.

Control flow: The command rejects negative IDs with stderr output, resolves the DB path through the parent, constructs `ContainerDatanodeDatabase`, and delegates display/analysis to `showContainerDetails`.

State and persistence behavior: It reads the SQLite database created by the parse command. It does not write state.

Dependencies and integration points: It is a query command over the container log database utility package.

Risks: A negative ID returns normally rather than failing the command. Most behavior is delegated to utility classes outside this work item.

Test signals: Error for negative ID and detailed per-container output for valid IDs in the DB.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ContainerInfoCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ContainerLogController.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ContainerLogController.java

Purpose: `ContainerLogController` groups container log parse/query commands and manages the inherited SQLite database path.

Important APIs and types: It extends `AbstractSubcommand`, uses picocli inherited `--db`, `Path`, `Files`, `Paths`, and `SQLDBConstants.DEFAULT_DB_FILENAME`.

Control flow: Subcommands are `info`, `parse`, `duplicate-open`, and `list`. `resolveDbPath()` uses a provided `--db` when present, validating parent directory existence, or falls back to `container_datanode.db` in the current directory if it exists.

State and persistence behavior: The controller stores the db path parameter. It does not create or mutate the DB; parse/query subcommands do that.

Dependencies and integration points: It is the common parent for all container log operations and centralizes default DB behavior.

Risks: When no `--db` is provided and no default file exists, query commands throw `IllegalArgumentException`. Provided paths are not required to already exist, allowing parse to create them.

Test signals: Correct default DB discovery message, exception for missing default DB, and parent-directory validation for explicit paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ContainerLogController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ContainerLogParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ContainerLogParser.java

Purpose: `ContainerLogParser` parses extracted container logs into a SQLite database used by the container log analysis commands.

Important APIs and types: It extends `AbstractSubcommand`, uses `ContainerLogController`, `ContainerDatanodeDatabase`, `ContainerLogFileParser`, `SQLDBConstants`, `Path`, `Files`, and picocli options `--path` and `--thread-count`.

Control flow: The command normalizes invalid non-positive thread counts to default 10, validates that `--path` is an existing directory, selects an explicit or default database path, validates parent directory existence, creates the raw log table, asks `ContainerLogFileParser` to process entries concurrently, populates the latest container log table, creates indexes, and prints success.

State and persistence behavior: It creates or updates a SQLite database, inserts parsed datanode/container transitions, derives latest container state rows, and creates indexes.

Dependencies and integration points: It is the ingestion entry point for all later `info`, `list`, and duplicate-open queries.

Risks: Invalid path or DB parent errors print and return normally rather than setting non-zero status. Parsing correctness is delegated to utility classes and log format patterns.

Test signals: Created DB tables/indexes, successful parse message, fallback default DB path, and invalid path/thread-count messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ContainerLogParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/DuplicateOpenContainersCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/DuplicateOpenContainersCommand.java

Purpose: `DuplicateOpenContainersCommand` lists containers with duplicate OPEN state entries in the parsed log database.

Important APIs and types: It implements `Callable<Void>`, uses parent `ContainerLogController`, and delegates to `ContainerDatanodeDatabase.findDuplicateOpenContainer`.

Control flow: The command resolves the DB path, constructs the database helper, calls the duplicate-open query/analysis method, and returns.

State and persistence behavior: It reads the SQLite database only.

Dependencies and integration points: It depends on tables populated by `ContainerLogParser` and analysis SQL/helper logic in utility classes.

Risks: All validation and output behavior is delegated; missing/invalid DB paths surface through the parent or database helper.

Test signals: Output listing container IDs and counts for duplicate OPEN states.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/DuplicateOpenContainersCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ListContainers.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ListContainers.java

Purpose: `ListContainers` queries parsed container-log data by lifecycle or supported health state.

Important APIs and types: It extends `AbstractSubcommand`, uses picocli `@ArgGroup(multiplicity = "1")` for mutually exclusive lifecycle/health selection, `ListLimitOptions`, `HddsProtos.LifeCycleState`, `ContainerHealthState`, and `ContainerDatanodeDatabase`.

Control flow: The command resolves the DB path, builds a database helper, and dispatches based on the chosen exclusive option. Lifecycle state calls `listContainersByState`; health state supports UNDER_REPLICATED and OVER_REPLICATED through `listReplicatedContainers`, UNHEALTHY through `listUnhealthyContainers`, and QUASI_CLOSED_STUCK through `listQuasiClosedStuckContainers`.

State and persistence behavior: It reads SQLite tables produced by the parser. No writes occur.

Dependencies and integration points: It exposes database analysis routines through CLI flags and uses common Ozone list-limit handling.

Risks: Unsupported health states print an error but do not fail. Exactly one selector is required by picocli, so command usability depends on arg group parsing.

Test signals: Correct database helper method for each state category, limit propagation, and unsupported health state message.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/ListContainers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/package-info.java

Purpose: This descriptor documents container log parsing and analysis commands.

Important APIs and types: It declares package `org.apache.hadoop.ozone.debug.logs.container`.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Used by generated package documentation.

Risks: Low; declaration matches source path.

Test signals: Build/package-info processing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/package-info.java -->
