# subset-b-008050 Research

Grouped research for Apache Ozone cli-admin SCM, datanode, container, pipeline, certificate, utility, and Recon namespace admin files. Each section preserves its source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeCheckSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeCheckSubcommand.java

## Purpose
Implements `ozone admin safemode status`, including HA-aware querying of a single SCM, a specifically requested SCM, or every SCM node in the configured service.

## Important APIs, Types, And Functions
The command is a picocli `Callable<Void>` with `--all/-a`, `--scm`, and `--service-id` through `ScmOption`. `call()` builds an `OzoneConfiguration`, discovers `serviceId` with `HddsUtils.getScmServiceId`, creates a `ContainerOperationClient` with a mutable `ScmNodeTarget`, and populates `SCMNodeInfo.buildNodeInfo`. Helper methods include `executeForSingleNode`, `findLeaderNode`, `executeForSpecificNode`, `executeForAllNodes`, `queryNode`, `matchesAddress`, and `printSafeModeRules`.

## Control Flow
In HA mode without `--all` or `--scm`, the command asks SCM for roles, parses role strings, matches the leader host or IP to configured SCM client addresses, sets `targetScmNode.nodeId`, and then calls `scmClient.inSafeMode()`. With `--all`, it loops through every `SCMNodeInfo`; with `--scm`, it filters by host or host:port. Verbose mode additionally prints `getSafeModeRuleStatuses()`.

## State And Persistence
The command persists no local state. It mutates the in-memory configuration via `ScmOption`, mutates `ScmNodeTarget` between RPCs, and reads SCM safe mode state and rule status from the cluster.

## Dependencies And Integration Points
It integrates with SCM HA metadata (`SCMNodeInfo`, `ScmNodeTarget`), `ScmClient` safe mode APIs, Ozone CLI error printing, and Apache Commons `StringUtils`/`Pair`.

## Risks And Test Signals
Role parsing depends on colon-delimited `getScmRoles()` strings and may fail if hostnames contain unexpected formatting. `queryNode` catches per-node exceptions and only prints errors, so multi-node failures may still exit successfully. Tests should cover HA leader selection, service ID requirements, `--all`, `--scm` host-only matching, verbose safe mode rule output, and RPC failure behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeCheckSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeCommands.java

## Purpose
Registers the `safemode` command group for SCM safe mode operations.

## Important APIs, Types, And Functions
`SafeModeCommands` implements `AdminSubcommand`, is annotated with picocli `@Command(name = "safemode")`, and declares `SafeModeCheckSubcommand`, `SafeModeExitSubcommand`, and `SafeModeWaitSubcommand` as subcommands. `@MetaInfServices(AdminSubcommand.class)` makes it discoverable by `OzoneAdmin`.

## Control Flow
There is no executable command logic in the class. Picocli dispatches to the selected child command after service-loader discovery.

## State And Persistence
No state is held or persisted.

## Dependencies And Integration Points
Depends on `AdminSubcommand`, `HddsVersionProvider`, picocli, and `org.kohsuke.MetaInfServices`.

## Risks And Test Signals
The main risk is registration drift: removing a child or annotation makes commands disappear. Test signals are CLI help output and service-loader command discovery for `ozone admin safemode`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeExitSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeExitSubcommand.java

## Purpose
Implements `ozone admin safemode exit`, a forced SCM safe mode exit operation.

## Important APIs, Types, And Functions
The class extends `ScmSubcommand` and implements `execute(ScmClient)`. It calls `scmClient.forceExitSafeMode()` and prints a success message only when the RPC returns true.

## Control Flow
`ScmSubcommand.call()` creates and closes the SCM client, then invokes `execute`. Any `IOException` from the force-exit RPC propagates through the CLI framework.

## State And Persistence
No local state is persisted. The command changes persistent cluster/SCM behavior by forcing safe mode off on the target SCM.

## Dependencies And Integration Points
Depends on `ScmClient.forceExitSafeMode`, `ScmSubcommand`, and picocli metadata. It shares address/service selection through `ScmOption` inherited by `ScmSubcommand`.

## Risks And Test Signals
This is an operationally risky command because it overrides normal safe mode rules. Tests should verify the RPC is invoked once, false return does not print a misleading success line, and failures produce a non-zero CLI result.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeExitSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeWaitSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeWaitSubcommand.java

## Purpose
Implements `ozone admin safemode wait`, polling SCM until safe mode ends or a timeout expires.

## Important APIs, Types, And Functions
The command is a picocli `Callable<Void>` with `-t/--timeout` seconds, `ScmOption`, `Time.monotonicNow`, and `ScmClient.inSafeMode()`. `getRemainingTimeInSec()` computes timeout budget from monotonic time.

## Control Flow
`call()` records start time, opens an SCM client, loops while remaining time is positive, checks `inSafeMode`, sleeps one second between checks, and retries after `InterruptedException`. On success it prints that SCM is out of safe mode; on timeout it throws `TimeoutException`.

## State And Persistence
No persistent state is written. It repeatedly opens clients and reads SCM safe mode state.

## Dependencies And Integration Points
Depends on `ScmOption`, `ScmClient`, Hadoop `Time`, and picocli. It is registered under `SafeModeCommands`.

## Risks And Test Signals
The `InterruptedException` path sleeps and then re-interrupts, which can cause the outer loop to continue with the interrupted flag set. Tests should cover zero/short timeout, successful transition, timeout exit code, unavailable SCM retries, and interruption behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeWaitSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ScmOption.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ScmOption.java

## Purpose
Provides reusable picocli options and client factories for commands that connect to SCM or SCM security services.

## Important APIs, Types, And Functions
Options are `--scm`, `--service-id`, and deprecated hidden `-id`. `createScmClient()` overloads create `ContainerOperationClient`, optionally with a supplied `OzoneConfiguration` and `ScmNodeTarget`. `checkAndSetSCMAddressArg` writes `OZONE_SCM_CLIENT_ADDRESS_KEY` and `OZONE_SCM_DEFAULT_SERVICE_ID`. `createScmSecurityClient()` delegates to `HddsServerUtil.getScmSecurityClient`.

## Control Flow
Client creation first applies command-line SCM address/service ID to configuration. If no service ID is provided or configured and no SCM client address can be derived, it throws `ConfigurationException`.

## State And Persistence
It mutates only the in-memory command configuration. The returned clients perform network RPCs but this mixin persists nothing itself.

## Dependencies And Integration Points
Integrates with Ozone configuration, `HddsUtils`, `ScmConfigKeys`, `ContainerOperationClient`, `SCMSecurityProtocol`, and SCM HA targeting.

## Risks And Test Signals
Configuration precedence and HA/non-HA validation are the core risks. Tests should cover explicit `--scm`, explicit `--service-id`, deprecated `-id`, missing non-HA address, HA default service ID behavior, and security client exception wrapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ScmOption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ScmSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ScmSubcommand.java

## Purpose
Defines the base class for SCM admin subcommands that need an `ScmClient`.

## Important APIs, Types, And Functions
`ScmSubcommand` extends `AbstractSubcommand` and implements `Callable<Void>`. It mixes in `ScmOption`, declares abstract `execute(ScmClient)`, and finalizes `call()` to create, use, and close a client.

## Control Flow
Picocli invokes `call`; the base class opens a client via `scmOption.createScmClient()`, calls subclass `execute`, and closes the client using try-with-resources.

## State And Persistence
No state is stored beyond the injected options. State changes are entirely in subclass RPCs.

## Dependencies And Integration Points
Used by most SCM command implementations in this work item: safe mode exit, topology, container, datanode, and pipeline commands.

## Risks And Test Signals
The final `call()` makes subclass execution simple but prevents subclasses from owning custom client lifecycle unless they do not extend it. Tests should verify clients are closed on success and exception and that subclass IOExceptions propagate.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ScmSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/TopologySubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/TopologySubcommand.java

## Purpose
Implements `ozone admin printTopology`, displaying SCM's datanode network topology in text or JSON with optional ordering and state filtering.

## Important APIs, Types, And Functions
Options include `--order`, `--full`, `--operational-state`, `--node-state`, and `--json`. It queries `ScmClient.queryNode` for `HEALTHY`, `STALE`, and `DEAD`, filters operational and health states, and formats via `printOrderedByLocation`, `printNodesWithLocation`, `formatPortOutput`, and nested JSON DTOs `NodeTopologyOrder`, `NodeTopologyDefault`, and `NodeTopologyFull`.

## Control Flow
For each node state, the command queries SCM cluster-wide, applies optional string-validated filters, then prints either by network location or by node list. JSON mode serializes DTO collections through `JsonUtils`; text mode prints state headings and datanode address/port/operational data.

## State And Persistence
No state is persisted. Runtime state is local collections of nodes, locations, and JSON wrappers.

## Dependencies And Integration Points
Depends on `DatanodeDetails`, `HddsProtos.Node`, Jackson serializers, `JsonUtils`, SCM node query APIs, and service-loader registration as an `AdminSubcommand`.

## Risks And Test Signals
State validation is manual string comparison and error messages can reference the wrong variable. `node.getNodeOperationalStates(0)` and `getNodeStates(0)` assume at least one entry. Tests should cover filters, ordered/unordered output, full JSON port serialization, empty topology, and malformed states.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/TopologySubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/CertCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/CertCommands.java

## Purpose
Registers the `cert` command group for SCM CA certificate operations.

## Important APIs, Types, And Functions
`CertCommands` implements `AdminSubcommand`, uses picocli `@Command(name = "cert")`, and declares `InfoSubcommand`, `ListSubcommand`, and `CleanExpiredCertsSubcommand`. `@MetaInfServices` exposes it to the admin CLI.

## Control Flow
The class has no executable logic; picocli dispatches to child commands.

## State And Persistence
No state is held or persisted.

## Dependencies And Integration Points
Integrates with `OzoneAdmin` via the `AdminSubcommand` service-loader mechanism.

## Risks And Test Signals
Test CLI help and command discovery to ensure certificate subcommands remain registered.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/CertCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/CleanExpiredCertsSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/CleanExpiredCertsSubcommand.java

## Purpose
Implements `ozone admin cert clean`, removing expired certificates from SCM metadata.

## Important APIs, Types, And Functions
The command extends `ScmCertSubcommand` and implements `execute(SCMSecurityProtocol)`. It calls `removeExpiredCertificates()` and prints the returned PEM list using `printCertList`.

## Control Flow
`ScmCertSubcommand.call()` creates the SCM security client, then this command removes expired certificates and formats the certificates that were removed.

## State And Persistence
The command mutates SCM certificate metadata by deleting expired certificate entries. Local state is not persisted.

## Dependencies And Integration Points
Depends on `SCMSecurityProtocol.removeExpiredCertificates`, `CertificateCodec` indirectly through `printCertList`, and SCM security client creation through `ScmOption`.

## Risks And Test Signals
The output says "List of removed expired certificates" even when none are removed. Tests should cover empty result, malformed returned PEM entries, security authorization failure, and that only expired certificates are removed server-side.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/CleanExpiredCertsSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/InfoSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/InfoSubcommand.java

## Purpose
Implements `ozone admin cert info`, printing details for one certificate serial ID.

## Important APIs, Types, And Functions
The command takes a required `serialId` parameter, calls `SCMSecurityProtocol.getCertificate(serialId)`, checks non-null with `Objects.requireNonNull`, parses PEM with `CertificateCodec.getX509Certificate`, and prints the `X509Certificate`.

## Control Flow
The command fetches the PEM string from SCM, prints the requested ID, then converts and prints certificate details. Certificate parse failures are logged to stderr and rethrown as `IOException`.

## State And Persistence
No local or cluster state is changed; it reads certificate metadata from SCM.

## Dependencies And Integration Points
Depends on SCM security protocol, Java X509 APIs, and Ozone certificate codec.

## Risks And Test Signals
Missing certificates become `NullPointerException` via `requireNonNull`, which may be less CLI-friendly than a checked error. Tests should cover found, not found, invalid PEM, and authorization failure cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/InfoSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/ListSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/ListSubcommand.java

## Purpose
Implements `ozone admin cert list`, listing SCM-issued certificates by role with text or JSON formatting.

## Important APIs, Types, And Functions
Options include `--start`, `--count`, `--role`, deprecated `--type`, and `--json`. `parseCertRole` maps `om`, `scm`, and other values to `HddsProtos.NodeType`. `execute` calls `SCMSecurityProtocol.listCertificate`, warns when the batch is full, and formats PEMs. Nested `Certificate` parses `X509Certificate` into serial, validity, subject DN, and issuer DN maps.

## Control Flow
The command chooses node type, fetches up to `count` certificates from `startSerialId`, then either prints tabular PEM-derived rows through `printCertList` or serializes parsed DTOs as JSON.

## State And Persistence
It is read-only against SCM certificate state.

## Dependencies And Integration Points
Depends on SCM security RPCs, `CertificateCodec`, Jackson serializers, `JsonUtils`, and `ScmCertSubcommand`.

## Risks And Test Signals
Unrecognized roles silently default to datanode. DN parsing splits on commas and equals signs and may mis-handle escaped DN components. Tests should cover role mapping, full-batch warning, JSON parse failures, deprecated option compatibility, and large serial values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/ListSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/ScmCertSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/ScmCertSubcommand.java

## Purpose
Provides the base class for certificate commands that connect to SCM security protocol and share certificate list formatting.

## Important APIs, Types, And Functions
`ScmCertSubcommand` implements `Callable<Void>`, mixes in `ScmOption`, declares abstract `execute(SCMSecurityProtocol)`, and provides `printCertList` and `printCert(X509Certificate)` using a fixed column format.

## Control Flow
`call()` creates an SCM security client, invokes subclass logic, and returns. `printCertList` prints an empty message or parses each PEM certificate and prints certificate fields, logging parse failures to stderr.

## State And Persistence
No state is persisted. The client may read or mutate certificate state depending on subclass.

## Dependencies And Integration Points
Used by `cert info`, `cert list`, and `cert clean`; depends on `SCMSecurityProtocol`, `CertificateCodec`, and Java X509 APIs.

## Risks And Test Signals
Unlike `ScmSubcommand`, the security client is not closed in this base class. Formatting uses wide fixed columns that can be awkward for long DNs. Tests should cover parse failures, empty lists, and client lifecycle expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/ScmCertSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/package-info.java

## Purpose
Documents the SCM CA certificate command package.

## Important APIs, Types, And Functions
There are no executable APIs; the package Javadoc says it contains SCM CA certificate commands.

## Control Flow
No control flow exists.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Javadoc integrates with source documentation for the `cert` command package.

## Risks And Test Signals
Only documentation drift is relevant; compile/Javadoc generation is the signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/cert/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/CloseSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/CloseSubcommand.java

## Purpose
Implements `ozone admin container close`, manually closing a container by ID.

## Important APIs, Types, And Functions
The command extends `ScmSubcommand`, has a required long `containerId` parameter, and calls `ScmClient.closeContainer(containerId)`.

## Control Flow
The base class opens an SCM client; `execute` sends the close RPC and lets exceptions propagate.

## State And Persistence
It mutates SCM/container lifecycle state by requesting a close transition.

## Dependencies And Integration Points
Depends on `ScmClient.closeContainer`, picocli parameter binding, and SCM lifecycle validation.

## Risks And Test Signals
There is no local validation for positive IDs or output on success. Tests should cover invalid IDs, missing ID, already closed/open container behavior, and server-side permission failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/CloseSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ContainerCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ContainerCommands.java

## Purpose
Registers the `container` command group for SCM container operations.

## Important APIs, Types, And Functions
`ContainerCommands` implements `AdminSubcommand`, uses `@Command(name = "container")`, and declares list, info, create, close, report, upgrade, and reconcile subcommands.

## Control Flow
It has no runtime logic; picocli handles subcommand dispatch after service-loader discovery.

## State And Persistence
No state is held or persisted.

## Dependencies And Integration Points
Integrates with `OzoneAdmin` via `@MetaInfServices(AdminSubcommand.class)`.

## Risks And Test Signals
Command visibility depends on this registration. Tests should verify admin help and each child command route.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ContainerCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ContainerIDParameters.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ContainerIDParameters.java

## Purpose
Provides reusable positional/stdin parsing and validation for commands that accept one or more container IDs.

## Important APIs, Types, And Functions
`ContainerIDParameters` extends `ItemsFromStdin`. `setContainerIDs` binds `0..*` parameters. `getValidatedIDs(boolean required)` enforces required input, parses positive longs, reports invalid tokens, and deduplicates while preserving first-seen order through `LinkedHashSet`.

## Control Flow
Commands call `getValidatedIDs`; if no IDs are supplied and stdin was not used, it throws `MissingParameterException`. It accumulates invalid inputs before throwing a picocli `ParameterException`.

## State And Persistence
Input tokens are held in the inherited item list. Nothing is persisted.

## Dependencies And Integration Points
Used by container info, report suppression, and reconcile commands. Depends on `ItemsFromStdin` and picocli command spec.

## Risks And Test Signals
Long parsing rejects non-decimal and overflow values. Required=false callers can receive an empty list. Tests should cover stdin marker behavior, duplicate IDs, zero/negative IDs, mixed valid/invalid inputs, and missing required parameters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ContainerIDParameters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/CreateSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/CreateSubcommand.java

## Purpose
Implements `ozone admin container create`, creating a new container through SCM with optional replication settings.

## Important APIs, Types, And Functions
Options include `--owner` and `ShellReplicationOptions`. `execute` derives `ReplicationConfig` from command params or configuration, defaults to `STAND_ALONE`/`ONE` when absent, and calls `ScmClient.createContainer(replicationConfig, owner)`.

## Control Flow
The command parses replication configuration, falls back to the legacy default, sends the create RPC, and prints the new container ID and replication config.

## State And Persistence
It mutates SCM state by allocating container metadata and a pipeline. Local state is transient.

## Dependencies And Integration Points
Depends on `ShellReplicationOptions`, `ReplicationConfig`, `HddsProtos`, `ContainerWithPipeline`, and SCM allocation APIs.

## Risks And Test Signals
It constructs a new `OzoneConfiguration` instead of reusing the command's loaded configuration, which may miss CLI/config context. Tests should cover default replication, Ratis/EC parsing, owner propagation, and allocation failure handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/CreateSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/InfoSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/InfoSubcommand.java

## Purpose
Implements `ozone admin container info`, printing container metadata, pipeline information, write pipeline state, datanodes, and replicas for one or more container IDs.

## Important APIs, Types, And Functions
Options include `--json` and `ContainerIDParameters`. It uses `getContainerWithPipeline`, `getContainerReplicas`, `getPipeline`, JSON wrappers `ContainerWithPipelineAndReplicas`/`ContainerWithoutDatanodes`, and `PipelineWithoutDatanodes` for empty pipelines.

## Control Flow
The command validates all IDs first, optionally prints JSON array delimiters for multiple IDs, then processes each container. It fetches container/pipeline data, separately tries replica fetch, handles missing write pipeline as CLOSED, and prints text or JSON.

## State And Persistence
Read-only against SCM/container metadata. It maintains only output formatting flags.

## Dependencies And Integration Points
Depends on SCM container and pipeline APIs, `SCMHAUtils.unwrapException`, `PipelineNotFoundException`, `HddsUtils.formatAccessControlExceptionLine`, `JsonUtils`, and `ContainerReplicaInfo`.

## Risks And Test Signals
Per-container lookup failures are printed and processing continues, possibly with successful exit. JSON for multiple containers is manually comma-delimited and can be invalid if an item prints only an error. Tests should cover multiple IDs, missing container, missing replica info, closed write pipeline, authorization errors, empty pipeline JSON, and replica sorting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/InfoSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ListSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ListSubcommand.java

## Purpose
Implements `ozone admin container list`, streaming container metadata as JSON with filters for ID range, count, lifecycle state, replication type/config, suppression status, and all-container pagination.

## Important APIs, Types, And Functions
Options include `--start`, `--count`, `--all`, `--state`, `--type`, `--replication/--factor`, and `--suppressed`. It parses `ReplicationConfig`, reads `OZONE_SCM_CONTAINER_LIST_MAX_COUNT`, calls `ScmClient.listContainer`, and writes `ContainerInfo` objects with a Jackson `SequenceWriter`.

## Control Flow
If replication is set without type, type defaults to RATIS. Non-`--all` mode caps count to the configured maximum, fetches one batch, writes JSON array entries, and warns if more exist. `--all` mode fetches batches starting after the last returned container ID until empty.

## State And Persistence
Read-only against SCM container metadata. It maintains the current pagination start ID.

## Dependencies And Integration Points
Depends on SCM list APIs, Ozone configuration, Jackson Java time module, `JsonUtils.getStdoutSequenceWriter`, and `ReplicationConfig.parse`.

## Risks And Test Signals
`--all` uses the user count as batch size and does not cap it against SCM maximum; count <= 0 in all mode falls back to max. JSON is the only output shape despite no `--json` option. Tests should cover filters, max-count warning, pagination gaps, suppression tri-state, EC/Ratis replication parsing, and empty results.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ListSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ReconcileSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ReconcileSubcommand.java

## Purpose
Implements `ozone admin container reconcile`, triggering replica checksum reconciliation or reporting reconciliation status.

## Important APIs, Types, And Functions
Options include `ContainerIDParameters` and `--status`. Trigger mode calls `ScmClient.reconcileContainer`. Status mode calls `getContainer`, validates closed Ratis containers, fetches replicas, and writes `ContainerWrapper` JSON through `SequenceWriter`. Nested wrappers expose datanode identity, replica state/index, and checksum with `JsonUtils.ChecksumSerializer`.

## Control Flow
`execute` branches on `--status`. Trigger mode loops IDs, prints successes, accumulates failures, and throws if any failed. Status mode validates all IDs first, streams status objects, buffers human-readable errors until JSON is flushed, and throws if any container failed.

## State And Persistence
Trigger mode mutates datanode/container reconciliation workflow state. Status mode is read-only.

## Dependencies And Integration Points
Depends on SCM reconciliation RPCs, `ContainerInfo`, `ContainerReplicaInfo`, Jackson annotations, `JsonUtils`, and Ozone access-control formatting.

## Risks And Test Signals
Status is client-side limited to non-open Ratis containers; future EC support requires updates. `getExceptionMessage` assumes non-null messages. Tests should cover open/EC containers, partial failures, checksum match calculation, authentication failures, JSON array validity, and trigger failure exit status.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ReconcileSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ReportSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ReportSubcommand.java

## Purpose
Implements `ozone admin container report`, displaying Replication Manager's container health summary and managing report suppression for specific containers.

## Important APIs, Types, And Functions
Options include mutually exclusive `--suppress/--unsuppress`, `--json`, and `ContainerIDParameters`. `printReport` calls `ScmClient.getReplicationManagerReport`; `handleSuppressUnsuppress` calls `suppressContainers`; output helpers print state summaries, health summaries, and sample container IDs.

## Control Flow
If suppress options are present, the command validates IDs and toggles suppression status. Otherwise it rejects positional IDs, fetches the report, warns when report timestamp is zero, emits JSON or text sections, and prints sample unhealthy containers.

## State And Persistence
Report mode is read-only. Suppress/unsuppress changes SCM report suppression metadata that affects future Replication Manager reports.

## Dependencies And Integration Points
Depends on `ReplicationManagerReport`, `ContainerHealthState`, `ContainerID`, SCM report APIs, and picocli arg groups.

## Risks And Test Signals
Timestamp conversion uses epoch seconds from milliseconds division, losing milliseconds but acceptable for display. Suppression partial failures throw after printing mixed results. Tests should cover no report yet, JSON shape, suppress/unsuppress validation, IDs without suppression, and sample-limit output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ReportSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/UpgradeSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/UpgradeSubcommand.java

## Purpose
Provides a deprecated placeholder for the old `ozone admin container upgrade` command, directing users to the repair command.

## Important APIs, Types, And Functions
The command extends `AbstractSubcommand`, implements `Callable<Void>`, accepts ignored `--volume` and `--yes` options, and always throws `IllegalStateException` from `call()`.

## Control Flow
Any invocation fails immediately with a message pointing to `ozone repair datanode upgrade-container-schema`.

## State And Persistence
No state is read or mutated.

## Dependencies And Integration Points
Maintains backward command discovery under `ContainerCommands` while moving functionality elsewhere.

## Risks And Test Signals
Tests should verify old options remain parseable and invocation fails with the migration message rather than performing any upgrade work.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/UpgradeSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/package-info.java

## Purpose
Documents the SCM container command package.

## Important APIs, Types, And Functions
No executable APIs are present; the package comment identifies container-related SCM commands.

## Control Flow
No control flow exists.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Javadoc-only integration for the container CLI package.

## Risks And Test Signals
Documentation drift is the only concern; compile/Javadoc generation is the signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/AbstractDiskBalancerSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/AbstractDiskBalancerSubCommand.java

## Purpose
Provides the shared execution framework for datanode DiskBalancer subcommands across explicit datanode targets and batch `--in-service-datanodes` mode.

## Important APIs, Types, And Functions
It implements `Callable<Void>`, mixes in `DiskBalancerCommonOptions`, checks `HDDS_DATANODE_DISK_BALANCER_ENABLED_KEY`, resolves target datanodes, executes abstract `executeCommand(String)`, and delegates result display to `displayResults`. It also supplies `validateParameters`, `getActionName`, `getConfigurationMap`, JSON error result construction, and `formatDatanodeDisplayName`.

## Control Flow
`call()` verifies the feature flag, validates target selection, performs subclass validation, resolves targets from positional args or SCM's healthy IN_SERVICE datanodes, deduplicates, runs the command sequentially for each datanode, accumulates success/failure/JSON results, and emits either JSON or consolidated text.

## State And Persistence
It persists nothing locally. It caches batch display-name mappings and controls RPC fan-out to datanode DiskBalancer services.

## Dependencies And Integration Points
Depends on `ContainerOperationClient`, `DiskBalancerSubCommandUtil`, `JsonUtils`, Ozone config keys, and subclass RPC implementations.

## Risks And Test Signals
Errors generally print and return null rather than throwing, so shell exit status may not reflect validation failures. Batch execution is sequential and may be slow for large clusters. Tests should cover disabled feature flag, missing targets, batch target discovery, JSON success/failure arrays, duplicate targets, and subclass validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/AbstractDiskBalancerSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/BasicDatanodeInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/BasicDatanodeInfo.java

## Purpose
Defines a JSON-friendly DTO for datanode list output, optionally enriched with usage and volume-health fields.

## Important APIs, Types, And Functions
`BasicDatanodeInfo` wraps `DatanodeDetails`, health/op states, optional usage fields, volume counts, and failed volumes. The nested `Builder` builds from `HddsProtos.Node` and optional `withUsageInfo`. Getters are ordered with `@JsonProperty` and omit nullable or empty fields with Jackson annotations.

## Control Flow
Construction converts protobuf datanode details to `DatanodeDetails`, extracts first health and operational states, optional volume counters, and failed volume paths.

## State And Persistence
Immutable DTO after construction; no persistence.

## Dependencies And Integration Points
Used by `ListInfoSubcommand` for JSON and text rendering. Depends on Jackson annotations, `DatanodeDetails`, and `HddsProtos.Node`.

## Risks And Test Signals
The builder assumes `node.getNodeStates(0)` and `getNodeOperationalStates(0)` exist. Tests should cover nodes with optional volume fields, failed volumes, usage enrichment, JSON ordering/null omission, and malformed protobuf edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/BasicDatanodeInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DatanodeCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DatanodeCommands.java

## Purpose
Registers the `datanode` admin command group.

## Important APIs, Types, And Functions
`DatanodeCommands` implements `AdminSubcommand`, is annotated with `@Command(name = "datanode")`, and declares list, decommission, maintenance, recommission, status, usageinfo, and diskbalancer subcommands.

## Control Flow
No executable logic exists; picocli dispatches to child commands after service discovery.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Integrates with `OzoneAdmin` via `@MetaInfServices(AdminSubcommand.class)`.

## Risks And Test Signals
Command discovery and help output should be tested to catch accidental registration loss.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DatanodeCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DatanodeParameters.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DatanodeParameters.java

## Purpose
Provides positional/stdin datanode address parsing for DiskBalancer commands.

## Important APIs, Types, And Functions
`DatanodeParameters` extends `ItemsFromStdin`. `setDatanodes` binds `0..*` `<datanode address>` arguments and documents stdin usage. `getDatanodes` returns a defensive `ArrayList` copy of inherited items.

## Control Flow
Picocli populates items from arguments or stdin marker `-`; consumers retrieve the list through `DiskBalancerCommonOptions`.

## State And Persistence
Input addresses are stored only in memory for the command invocation.

## Dependencies And Integration Points
Used by `DiskBalancerCommonOptions` and all DiskBalancer subcommands.

## Risks And Test Signals
No address validation occurs here; validation/proxy creation is deferred. Tests should cover stdin, empty list with batch mode, host-only addresses, explicit ports, and duplicate preservation before base-class deduplication.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DatanodeParameters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DecommissionStatusSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DecommissionStatusSubCommand.java

## Purpose
Implements `ozone admin datanode status decommission`, showing progress and container details for nodes currently in DECOMMISSIONING.

## Important APIs, Types, And Functions
Options include `--json` and `NodeSelectionMixin`. It queries `ScmClient.queryNode(DECOMMISSIONING, ...)`, filters through `DecommissionUtils.getDecommissioningNodesList`, reads JMX metrics with `getMetrics`, derives counts with `DecommissionUtils.getCountsMap`, and fetches `getContainersOnDecomNode`.

## Control Flow
The command rejects `--hostname`, filters decommissioning nodes by node ID or IP when supplied, handles empty matches with stderr messages, gets NodeDecommissionMetrics JSON, then prints either JSON maps containing datanode details/metrics/containers or text sections per datanode.

## State And Persistence
Read-only against SCM node state, metrics, and container mappings.

## Dependencies And Integration Points
Depends on `DecommissionUtils`, `DatanodeDetails`, `ContainerID`, `JsonUtils`, SCM node query and metrics APIs, and `NodeSelectionMixin`.

## Risks And Test Signals
Metrics may be unavailable or mismatched to nodes; the command prints generic metric errors and continues. Tests should cover no decommissioning nodes, ID/IP filters, unsupported hostname, missing metrics JSON, container map output, and JSON conversion of container IDs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DecommissionStatusSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DecommissionSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DecommissionSubCommand.java

## Purpose
Implements `ozone admin datanode decommission`, starting decommission workflows for one or more hostnames.

## Important APIs, Types, And Functions
The command extends `ScmSubcommand`, mixes in `HostNameParameters`, has `--force`, calls `ScmClient.decommissionNodes(hosts, force)`, and shares static `showErrors`.

## Control Flow
It collects hostnames, sends one decommission request, prints all requested hosts, then prints per-node errors and throws `IOException` if SCM reported any failures.

## State And Persistence
It mutates SCM datanode operational state/workflow metadata. Local state is transient.

## Dependencies And Integration Points
Depends on SCM datanode admin APIs, `DatanodeAdminError`, and host parsing via `ItemsFromStdin`.

## Risks And Test Signals
It prints "Started decommissioning" before reporting per-node failures, so users must read stderr. Tests should cover multi-host partial failures, force flag propagation, stdin host lists, and non-zero exit on errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DecommissionSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerCommands.java

## Purpose
Registers the `datanode diskbalancer` command group and documents usage for start, stop, update, report, and status.

## Important APIs, Types, And Functions
`DiskBalancerCommands` is a picocli command with child subcommands `DiskBalancerStartSubcommand`, `DiskBalancerStopSubcommand`, `DiskBalancerUpdateSubcommand`, `DiskBalancerReportSubcommand`, and `DiskBalancerStatusSubcommand`.

## Control Flow
No command execution happens in this class; picocli routes to selected children.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Nested under `DatanodeCommands`; references `HDDS_DATANODE_DISK_BALANCER_ENABLED_KEY` in its description.

## Risks And Test Signals
The large embedded help text can drift from implementation. Tests should verify help output and that each subcommand is reachable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerCommonOptions.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerCommonOptions.java

## Purpose
Defines common options shared by all DiskBalancer datanode subcommands.

## Important APIs, Types, And Functions
It mixes in `DatanodeParameters`, exposes `--in-service-datanodes` and `--json`, and provides getters `getDatanodes`, `isInServiceDatanodes`, and `isJson`.

## Control Flow
Picocli populates the mixin before `AbstractDiskBalancerSubCommand.call()` reads it. `getDatanodes` returns an empty list when no positional mixin data is present, supporting batch mode without addresses.

## State And Persistence
Holds invocation options only.

## Dependencies And Integration Points
Used by all DiskBalancer subcommands through the abstract base class.

## Risks And Test Signals
Combining explicit datanodes with `--in-service-datanodes` is not rejected here; the base class chooses batch mode. Tests should cover JSON flag propagation, absent positional args, and mixed selection behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerCommonOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerReportSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerReportSubcommand.java

## Purpose
Implements `ozone admin datanode diskbalancer report`, retrieving volume-density and per-volume usage reports from one or more datanodes.

## Important APIs, Types, And Functions
Extends `AbstractDiskBalancerSubCommand`; `executeCommand` creates a `DiskBalancerProtocol` proxy and calls `getDiskBalancerInfo`. `generateReport` formats `DatanodeDiskBalancerInfoProto` and `VolumeReportProto`; `toJson` builds JSON maps with density, ideal usage, threshold range, and volume rows.

## Control Flow
For each target datanode, it fetches disk balancer info and either returns a JSON map or stores the proto in a concurrent map. After all targets, non-JSON mode prints failures and a report sorted by aggregate density descending.

## State And Persistence
Read-only against datanode DiskBalancer state. It caches fetched protos for consolidated output.

## Dependencies And Integration Points
Depends on datanode `DiskBalancerProtocol`, protobuf disk/volume reports, `DiskBalancerSubCommandUtil`, and Hadoop `StringUtils.byteDesc`.

## Risks And Test Signals
Formatting uses a dynamic `String.format` template and content list; mismatches could throw. Tests should cover nodes with no ideal usage, no volumes, failed nodes, JSON output, display name formatting, and percent calculations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerReportSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerStartSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerStartSubcommand.java

## Purpose
Implements `ozone admin datanode diskbalancer start`, starting DiskBalancer on selected datanodes with optional configuration overrides.

## Important APIs, Types, And Functions
Options include `--threshold-percentage`, `--bandwidth-in-mb`, `--parallel-thread`, `--stop-after-disk-even`, and `--container-states`. `buildConfigProto` creates `DiskBalancerConfigurationProto`; `executeCommand` calls `startDiskBalancer`.

## Control Flow
The abstract base validates targets and feature flag. For each datanode, this command opens a proxy, builds a config containing only supplied fields, starts DiskBalancer, returns a success JSON map, and closes the proxy. Text mode summarizes success/failure by batch or explicit target mode.

## State And Persistence
It mutates datanode-local DiskBalancer service state and configuration.

## Dependencies And Integration Points
Depends on `DiskBalancerProtocol.startDiskBalancer`, protobuf configuration, and shared display/config map helpers.

## Risks And Test Signals
There is no local validation for negative threshold, bandwidth, or threads, nor enum validation for `containerStates`. Tests should cover each config field, invalid values as handled by server, JSON success/error shape, batch success message, and proxy close on failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerStartSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerStatusSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerStatusSubcommand.java

## Purpose
Implements `ozone admin datanode diskbalancer status`, showing current DiskBalancer status, configuration, move counts, and estimated remaining work.

## Important APIs, Types, And Functions
Extends `AbstractDiskBalancerSubCommand`; calls `DiskBalancerProtocol.getDiskBalancerInfo`; `generateStatus` renders tabular status; `createStatusResult` builds JSON; `calculateEstimatedTimeLeft` derives minutes from bytes-to-move and configured MB/s.

## Control Flow
Each target is queried via a datanode proxy. JSON mode returns one map per datanode to the base class; text mode stores protos and later prints a consolidated table plus explanatory notes.

## State And Persistence
Read-only against datanode DiskBalancer state. Local cached status map is transient.

## Dependencies And Integration Points
Depends on `DatanodeDiskBalancerInfoProto`, `DiskBalancerConfigurationProto`, and `DiskBalancerSubCommandUtil`.

## Risks And Test Signals
It assumes `getDiskBalancerConf()` exists and divides by bandwidth, returning N/A when bandwidth is zero. Tests should cover zero bytes remaining, zero bandwidth, absent container states, failed node errors, JSON null estimate, and table formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerStatusSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerStopSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerStopSubcommand.java

## Purpose
Implements `ozone admin datanode diskbalancer stop`, stopping DiskBalancer on selected datanodes.

## Important APIs, Types, And Functions
Extends `AbstractDiskBalancerSubCommand`; `executeCommand` creates a `DiskBalancerProtocol` proxy, calls `stopDiskBalancer`, and returns a JSON success map with datanode/action/status.

## Control Flow
The base class resolves targets and calls this command for each. Text mode prints batch or explicit success/failure summaries; JSON mode output is handled by the base class.

## State And Persistence
It mutates datanode-local DiskBalancer running state by stopping the service/workflow.

## Dependencies And Integration Points
Depends on `DiskBalancerProtocol.stopDiskBalancer` and shared target/display handling.

## Risks And Test Signals
Stop failures are per-node and may still allow other nodes to be processed. Tests should cover already stopped service, unreachable node, JSON error result, batch all-success message, and proxy close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerStopSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerSubCommandUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerSubCommandUtil.java

## Purpose
Provides utility functions for DiskBalancer CLI commands, including datanode proxy creation and SCM-based target discovery.

## Important APIs, Types, And Functions
`getSingleNodeDiskBalancerProxy` parses host[:port] and creates `DiskBalancerProtocolClientSideTranslatorPB` with current user and `OzoneConfiguration`. `getAllOperableNodesClientRpcAddress` queries SCM for HEALTHY IN_SERVICE nodes and maps CLIENT_RPC addresses to display strings. `getDatanodeHostAndIp` formats a datanode protobuf into hostname/IP:port display text.

## Control Flow
Address parsing uses the default CLIENT_RPC port when no port is provided. Batch discovery iterates SCM nodes, extracts `DatanodeDetails`, skips DEAD nodes defensively, requires CLIENT_RPC port, and builds a deterministic `LinkedHashMap`.

## State And Persistence
No state is persisted. It creates network clients and reads SCM node metadata.

## Dependencies And Integration Points
Depends on `DiskBalancerProtocol`, `DiskBalancerProtocolClientSideTranslatorPB`, SCM query APIs, `DatanodeDetails.Port`, `NetUtils`, and `UserGroupInformation`.

## Risks And Test Signals
The simple `address.contains(":")` check is not IPv6-safe. Batch query already asks for HEALTHY but still checks DEAD. Tests should cover host-only default port, host:port, IPv6 or malformed addresses, missing CLIENT_RPC port, and hostname display formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerSubCommandUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerUpdateSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerUpdateSubcommand.java

## Purpose
Implements `ozone admin datanode diskbalancer update`, changing DiskBalancer configuration on selected datanodes.

## Important APIs, Types, And Functions
Options mirror start: threshold, bandwidth, parallel thread, stop-after-even, and container states. `validateParameters` requires at least one option. `buildConfigProto` creates `HddsProtos.DiskBalancerConfigurationProto`; `executeCommand` calls `updateDiskBalancerConfiguration`.

## Control Flow
After base validation, each datanode receives a config proto containing only fields supplied by the user. The command returns JSON success maps or prints consolidated text summaries.

## State And Persistence
It mutates datanode-local DiskBalancer configuration.

## Dependencies And Integration Points
Depends on `DiskBalancerProtocol.updateDiskBalancerConfiguration`, protobuf config, and base DiskBalancer target handling.

## Risks And Test Signals
Input range and container state validation are left to server-side logic. Tests should cover no options error, each option's inclusion, partial node failures, JSON configuration maps, batch mode, and proxy close on exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerUpdateSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/HostNameParameters.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/HostNameParameters.java

## Purpose
Provides hostname list parsing for datanode administrative workflows.

## Important APIs, Types, And Functions
`HostNameParameters` extends `ItemsFromStdin`; `setHostNames` binds required `1..*` host names and `getHostNames` returns the inherited item list.

## Control Flow
Picocli fills the list from command arguments or stdin; decommission, maintenance, and recommission commands pass it to SCM.

## State And Persistence
Hostnames live only for the invocation.

## Dependencies And Integration Points
Used by datanode admin lifecycle commands.

## Risks And Test Signals
No normalization or validation occurs here. Tests should cover missing hostnames, stdin usage, duplicate hosts, and hostnames with ports or unexpected forms as handled by SCM.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/HostNameParameters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/ListInfoSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/ListInfoSubcommand.java

## Purpose
Implements `ozone admin datanode list`, listing datanode state, pipeline associations, volume health, and optionally usage-enriched ordering.

## Important APIs, Types, And Functions
Options include operational/health state filters, `--json`, `--nodes-with-failed-volumes`, node selection through `ExclusiveNodeOptions`, `--most-used/--least-used`, and `ListLimitOptions`. It uses `BasicDatanodeInfo`, `ScmClient.listPipelines`, `queryNode`, and `getDatanodeUsageInfo`.

## Control Flow
The command rejects failed-volume filtering with node ID lookup, loads pipelines, handles single UUID lookup, otherwise streams all nodes or sorted usage info, applies IP/hostname/state/failed-volume filters, limits results unless `--all`, and prints JSON or text details with related pipelines.

## State And Persistence
Read-only against SCM node, pipeline, and usage state. It stores the pipeline list for text rendering.

## Dependencies And Integration Points
Depends on `NodeSelectionMixin`, `BasicDatanodeInfo`, SCM node/usage/pipeline APIs, `JsonUtils`, and shell `ListLimitOptions`.

## Risks And Test Signals
UUID parsing can throw for invalid IDs. Usage-sorted mode performs one `queryNode` per returned usage entry. Tests should cover all filters, limits, JSON/text, failed volume output, most/least used ordering, invalid UUID, and nodes with no related pipelines.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/ListInfoSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/MaintenanceSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/MaintenanceSubCommand.java

## Purpose
Implements `ozone admin datanode maintenance`, starting maintenance mode on one or more datanodes.

## Important APIs, Types, And Functions
The command extends `ScmSubcommand`, mixes in `HostNameParameters`, supports `--end` hours and `--force`, and calls `ScmClient.startMaintenanceNodes(hosts, endInHours, force)`.

## Control Flow
It sends the maintenance request for all hosts, prints the requested hosts, then delegates partial-failure handling to `DecommissionSubCommand.showErrors`.

## State And Persistence
It mutates SCM datanode operational state and may set a maintenance expiry timestamp.

## Dependencies And Integration Points
Depends on SCM datanode admin APIs and shared host/error handling.

## Risks And Test Signals
`--force` description mentions decommission instead of maintenance. There is no local validation for negative `--end`. Tests should cover expiry propagation, force flag, partial failures, and non-zero exit on errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/MaintenanceSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/NodeSelectionMixin.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/NodeSelectionMixin.java

## Purpose
Provides a standardized mutually exclusive datanode selector mixin for commands that can target a node by UUID, hostname, or IP.

## Important APIs, Types, And Functions
`NodeSelectionMixin` contains an exclusive `Selection` arg group. Public getters return effective node ID with precedence `--node-id` over deprecated hidden `--id` over deprecated hidden `--uuid`, plus hostname and IP values.

## Control Flow
Picocli enforces that at most one selector from the group is present. Commands read getters to filter/query SCM.

## State And Persistence
Holds only invocation selection values.

## Dependencies And Integration Points
Used by datanode list, usage, and decommission status commands.

## Risks And Test Signals
The arg group multiplicity allows no selector; some consumers require one via a subclass arg group. Tests should cover exclusivity, deprecated aliases, precedence, default empty strings, and command-specific unsupported selector handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/NodeSelectionMixin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/RecommissionSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/RecommissionSubCommand.java

## Purpose
Implements `ozone admin datanode recommission`, returning decommissioned or maintenance datanodes to service.

## Important APIs, Types, And Functions
The command extends `ScmSubcommand`, mixes in `HostNameParameters`, calls `ScmClient.recommissionNodes(hosts)`, and uses shared `showErrors`.

## Control Flow
It sends all hostnames to SCM, prints a started message for every requested host, then prints per-host errors and throws if SCM reported failures.

## State And Persistence
It mutates SCM datanode operational workflow state.

## Dependencies And Integration Points
Depends on SCM datanode admin APIs and `DatanodeAdminError`.

## Risks And Test Signals
The thrown message says "Some nodes could be recommissioned", likely missing "not". Tests should cover successful recommission, partial failures, stdin host input, and exit status.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/RecommissionSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/StatusSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/StatusSubCommand.java

## Purpose
Registers the `ozone admin datanode status` subgroup.

## Important APIs, Types, And Functions
`StatusSubCommand` is a picocli command with one child, `DecommissionStatusSubCommand`.

## Control Flow
No runtime logic exists in this class; picocli dispatches to child status commands.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Nested under `DatanodeCommands`; uses `HddsVersionProvider` for CLI version help.

## Risks And Test Signals
Tests should verify `datanode status decommission` remains reachable and help output lists it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/StatusSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/UsageInfoSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/UsageInfoSubcommand.java

## Purpose
Implements `ozone admin datanode usageinfo`, showing capacity, usage, reserved, committed, pipeline, and container counts for selected or most/least used datanodes.

## Important APIs, Types, And Functions
Options include required `NodeSelectionArguments` arg group, `--count`, and `--json`. It calls `ScmClient.getDatanodeUsageInfo(hostnameOrIp, nodeId)` for direct lookup or `getDatanodeUsageInfo(mostUsed, count)` for ranking. Nested `DatanodeUsage` converts `DatanodeUsageInfoProto` to printable/JSON fields and percentage getters.

## Control Flow
The command resolves IP/hostname/deprecated address versus node ID, validates count > 0, fetches usage protos, wraps them, then prints JSON or text sections. Text output includes filesystem stats when present and Ozone capacity breakdown always.

## State And Persistence
Read-only against SCM usage state.

## Dependencies And Integration Points
Depends on `NodeSelectionMixin`, SCM usage APIs, `DatanodeDetails`, Jackson serializers, `JsonUtils`, and Hadoop byte formatting.

## Risks And Test Signals
`getOzoneUsedRatio` and `getOzoneAvailableRatio` divide by ozone capacity without zero guard. The arg group allows ranking flags and selectors through inherited options. Tests should cover direct selectors, most/least used, invalid count, zero capacity, filesystem stats absent, JSON decimal serialization, and deprecated `--address`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/UsageInfoSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/package-info.java

## Purpose
Documents the SCM datanode command package.

## Important APIs, Types, And Functions
No executable APIs are present; the package comment identifies datanode-related SCM commands.

## Control Flow
No control flow exists.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Javadoc-only integration for datanode CLI code.

## Risks And Test Signals
Documentation drift only; compile/Javadoc generation is enough.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/package-info.java

## Purpose
Documents the top-level SCM CLI package.

## Important APIs, Types, And Functions
No executable APIs are present; the package comment identifies SCM CLI tools.

## Control Flow
No control flow exists.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Javadoc documentation for `org.apache.hadoop.hdds.scm.cli`.

## Risks And Test Signals
Documentation drift only; compile/Javadoc generation is the signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/ActivatePipelineSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/ActivatePipelineSubcommand.java

## Purpose
Implements `ozone admin pipeline activate`, activating a specific pipeline through SCM.

## Important APIs, Types, And Functions
The command extends `ScmSubcommand`, accepts a pipeline ID parameter, builds `HddsProtos.PipelineID`, and calls `ScmClient.activatePipeline`.

## Control Flow
The base class opens the SCM client; `execute` sends one activation RPC.

## State And Persistence
It mutates SCM pipeline lifecycle state.

## Dependencies And Integration Points
Depends on SCM pipeline APIs and protobuf `PipelineID`.

## Risks And Test Signals
No local UUID validation or success message exists. Tests should cover valid/invalid pipeline IDs, already active/closed states, permission failures, and RPC propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/ActivatePipelineSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/ClosePipelineSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/ClosePipelineSubcommand.java

## Purpose
Implements `ozone admin pipeline close`, closing one pipeline or all non-closed pipelines optionally filtered by replication config.

## Important APIs, Types, And Functions
It uses a required arg group containing either pipeline ID or `--all`, plus `FilterPipelineOptions`. Single-ID mode calls `closePipeline`; all mode lists pipelines, filters out CLOSED and optionally applies replication predicate, then closes each.

## Control Flow
If a specific pipeline ID is provided with replication filters, it throws. In `--all`, it builds a list from `scmClient.listPipelines`, prints a count, and attempts to close each, logging per-pipeline IOExceptions without aborting the loop.

## State And Persistence
It mutates SCM pipeline lifecycle state by requesting close transitions.

## Dependencies And Integration Points
Depends on `ScmClient.listPipelines`, `closePipeline`, `FilterPipelineOptions`, Guava `Strings`, and `Pipeline` state/config APIs.

## Risks And Test Signals
Per-pipeline failures in `--all` only print to stderr and do not cause a non-zero exit. Tests should cover arg-group exclusivity, filters with single ID rejection, all-mode filtering, closed pipelines ignored, and partial close failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/ClosePipelineSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/CreatePipelineSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/CreatePipelineSubcommand.java

## Purpose
Implements `ozone admin pipeline create`, creating a replication pipeline.

## Important APIs, Types, And Functions
Options include replication type (hidden/deprecated full name aliases) and replication factor. `execute` rejects CHAINED, EC, and STAND_ALONE, then calls `ScmClient.createReplicationPipeline(type, factor, NodePool.getDefaultInstance())`.

## Control Flow
After validation, SCM creates a RATIS pipeline and the command prints the created ID and full pipeline string when non-null.

## State And Persistence
It mutates SCM pipeline metadata by allocating a new pipeline.

## Dependencies And Integration Points
Depends on `HddsProtos.ReplicationType`, `ReplicationFactor`, `NodePool`, and SCM pipeline allocation.

## Risks And Test Signals
The description says replication type is RATIS while still accepting a hidden type option. Tests should cover unsupported types, factor values, null return, creation failure, and output format.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/CreatePipelineSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/DeactivatePipelineSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/DeactivatePipelineSubcommand.java

## Purpose
Implements `ozone admin pipeline deactivate`, deactivating a specific pipeline through SCM.

## Important APIs, Types, And Functions
The command accepts a pipeline ID parameter, builds `HddsProtos.PipelineID`, and calls `ScmClient.deactivatePipeline`.

## Control Flow
`ScmSubcommand` handles client lifecycle; `execute` performs one deactivate RPC.

## State And Persistence
It mutates SCM pipeline lifecycle state.

## Dependencies And Integration Points
Depends on SCM pipeline APIs and protobuf IDs.

## Risks And Test Signals
No local ID validation or success output. Tests should cover valid/invalid pipeline IDs, already inactive/closed behavior, and permission/RPC failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/DeactivatePipelineSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/FilterPipelineOptions.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/FilterPipelineOptions.java

## Purpose
Provides reusable pipeline replication filters for list and close commands.

## Important APIs, Types, And Functions
Options include `--type`, `--replication`, deprecated `--filterByFactor/--filter-by-factor`, and hidden deprecated `-ffc`. `getReplicationFilter` returns an optional `Predicate<Pipeline>` based on exact `ReplicationConfig` or replication type string.

## Control Flow
Factor and replication are mutually exclusive. Replication requires replication type and is parsed with `ReplicationConfig.parse`. Type-only mode compares pipeline replication type case-insensitively. With no filter options, it returns `Optional.empty()`.

## State And Persistence
Holds only parsed invocation options.

## Dependencies And Integration Points
Used by `ListPipelinesSubcommand` and `ClosePipelineSubcommand`. Depends on Ozone replication config classes and `Pipeline.getReplicationConfig`.

## Risks And Test Signals
Invalid type names throw `IllegalArgumentException`. Type comparison uses string names rather than enum parsing. Tests should cover factor alias, EC replication string parsing, missing type with replication, mutually exclusive options, and case-insensitive type filtering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/FilterPipelineOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/ListPipelinesSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/ListPipelinesSubcommand.java

## Purpose
Implements `ozone admin pipeline list`, listing pipelines with optional state and replication filters in text or JSON.

## Important APIs, Types, And Functions
Uses `FilterPipelineOptions`, `--state` plus deprecated aliases, hidden `-fst`, and `--json`. It calls `ScmClient.listPipelines`, filters with Java streams, and serializes JSON through `JsonUtils`.

## Control Flow
The command creates a stream from all pipelines, applies replication predicate when present, applies state string filter when present, then either collects to a list for JSON output or prints each pipeline's `toString`.

## State And Persistence
Read-only against SCM pipeline metadata.

## Dependencies And Integration Points
Depends on SCM pipeline list API, `FilterPipelineOptions`, Guava `Strings`, `Pipeline`, and `JsonUtils`.

## Risks And Test Signals
State filtering is free-form string comparison, so typos silently produce empty output. Tests should cover replication filters, deprecated state alias, JSON output, empty list, and mixed case states.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/ListPipelinesSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/PipelineCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/PipelineCommands.java

## Purpose
Registers the `pipeline` SCM admin command group.

## Important APIs, Types, And Functions
`PipelineCommands` implements `AdminSubcommand`, is annotated with `@Command(name = "pipeline")`, and declares list, activate, deactivate, create, and close subcommands.

## Control Flow
No executable logic exists; picocli dispatches to child commands.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Integrates with `OzoneAdmin` via `@MetaInfServices(AdminSubcommand.class)`.

## Risks And Test Signals
Command registration should be covered by CLI help/discovery tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/PipelineCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/package-info.java

## Purpose
Documents the SCM pipeline command package.

## Important APIs, Types, And Functions
No executable APIs are present; the package comment identifies pipeline-related SCM commands.

## Control Flow
No control flow exists.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Javadoc-only integration for pipeline CLI code.

## Risks And Test Signals
Documentation drift only; compile/Javadoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/pipeline/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/util/DurationUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/util/DurationUtil.java

## Purpose
Provides a small utility for formatting `Duration` values as compact human-readable strings.

## Important APIs, Types, And Functions
`DurationUtil` is final with a private constructor. `getPrettyDuration(Duration)` returns strings like `1h 30m 45s`, `2m 30s`, or `30s` based on whole seconds.

## Control Flow
The method calculates hours, minutes, and seconds from `duration.getSeconds()`. It prefers hours output, then minutes output, then non-negative seconds, otherwise throws `IllegalStateException`.

## State And Persistence
Stateless and pure for non-negative durations.

## Dependencies And Integration Points
Depends only on `java.time.Duration` and `String.format`. It is available to CLI code needing duration display.

## Risks And Test Signals
Negative durations throw only when seconds is negative; nanosecond-only negative edge cases should be considered. Tests should cover zero, sub-minute, minute, hour, multi-hour, and negative durations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/util/DurationUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/util/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/util/package-info.java

## Purpose
Documents the CLI utility package.

## Important APIs, Types, And Functions
No executable APIs are present; the package comment identifies SCM-related CLI utilities.

## Control Flow
No control flow exists.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Javadoc-only documentation for `org.apache.hadoop.hdds.util` in the cli-admin module.

## Risks And Test Signals
Documentation drift only; compile/Javadoc generation is enough.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/OzoneAdmin.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/OzoneAdmin.java

## Purpose
Defines the `ozone admin` CLI entrypoint and extensible parent command for admin operations.

## Important APIs, Types, And Functions
`OzoneAdmin` extends `Shell` and implements `ExtensibleParentCommand`. `main` runs the shell. `subcommandType()` returns `AdminSubcommand.class`, enabling service-loaded admin subcommands.

## Control Flow
The JVM entrypoint instantiates `OzoneAdmin` and delegates argument parsing/execution to `Shell.run`. The shell discovers implementations of `AdminSubcommand` and registers them as children.

## State And Persistence
No persistent state is stored. It owns command-line configuration context inherited from `Shell`.

## Dependencies And Integration Points
Integrates all `@MetaInfServices(AdminSubcommand.class)` command groups in this module and elsewhere.

## Risks And Test Signals
Changing `subcommandType` or annotations would break command discovery. Tests should cover main invocation, alias `admin`, help output, and service-loaded child command availability.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/OzoneAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/DiskUsageSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/DiskUsageSubCommand.java

## Purpose
Implements `ozone admin namespace du`, querying Recon for namespace disk usage and printing path totals and immediate subpath rows.

## Important APIs, Types, And Functions
Options include path, `--file`, `--replica`, `--no-header`, `ListLimitOptions`, and `PrefixFilterOption`. It calls `NSSummaryCLIUtils.makeHttpCall` against `/api/v1/namespace/usage`, parses JSON with `JsonUtils`, formats sizes with `FileUtils.byteCountToDisplaySize`, and prints aligned rows.

## Control Flow
The command rejects empty path, builds the Recon URL, calls Recon with parsed OFS path, handles null response and `PATH_NOT_FOUND`, prints optional header totals, then iterates `subPaths` up to limit and prefix filter, appending `/` to directory paths.

## State And Persistence
Read-only against Recon namespace summary state.

## Dependencies And Integration Points
Depends on `NSSummaryAdmin` for Recon address/security config, `NSSummaryCLIUtils`, Recon REST API, Ozone key prefix constants, list-limit and prefix-filter shell mixins.

## Risks And Test Signals
URL query parameters are appended without URL encoding. Prefix filtering happens client-side after Recon returns data. Tests should cover root path, OFS path parsing, path-not-found, empty objects, replica sizes, no-header, prefix filtering, file listing, and limit enforcement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/DiskUsageSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/FileSizeDistSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/FileSizeDistSubCommand.java

## Purpose
Implements `ozone admin namespace dist`, querying Recon for file-size distribution under a namespace path.

## Important APIs, Types, And Functions
The command accepts a required-ish path, calls `/api/v1/namespace/dist`, parses `dist` JSON bins, converts bin indexes to byte ranges using powers of two, and prints percentage/count rows.

## Control Flow
It rejects empty path, calls Recon, handles null response, `PATH_NOT_FOUND`, and `TYPE_NOT_APPLICABLE`, sums distribution bins, prints an empty-object message when all bins are zero, and prints non-zero bins as readable ranges.

## State And Persistence
Read-only against Recon namespace summary data.

## Dependencies And Integration Points
Depends on `NSSummaryAdmin`, `NSSummaryCLIUtils`, Recon REST, `JsonUtils`, and `FileUtils`.

## Risks And Test Signals
This command passes `path` directly rather than `parseInputPath`, unlike summary/du, so OFS paths may behave differently. Tests should cover OFS paths, empty distribution, type-not-applicable, non-zero bins, and percentage rounding.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/FileSizeDistSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/NSSummaryAdmin.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/NSSummaryAdmin.java

## Purpose
Registers the `namespace` admin command group and computes the Recon web base URL used by namespace summary commands.

## Important APIs, Types, And Functions
`NSSummaryAdmin` implements `AdminSubcommand`, declares summary, du, quota, and dist subcommands, and exposes `getReconWebAddress`, `isHTTPSEnabled`, and `getOzoneConfig`. Helpers split host and port from config addresses.

## Control Flow
`getReconWebAddress` reads HTTP policy, chooses HTTP or HTTPS Recon address defaults, detects default wildcard host, and if default, replaces host with Recon RPC host while preserving web port. It returns `http(s)://host:port`.

## State And Persistence
No state is persisted. It reads Ozone configuration from the parent `OzoneAdmin`.

## Dependencies And Integration Points
Depends on Recon config keys, `HttpConfig`, `HttpServer2` scheme constants, `OzoneAdmin`, and service-loader registration.

## Risks And Test Signals
`getPort` assumes an address contains `:` and may not handle IPv6 bracket forms. Tests should cover HTTP and HTTPS policies, default host fallback, custom web host, RPC host fallback, and malformed config values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/NSSummaryAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/NSSummaryCLIUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/NSSummaryCLIUtils.java

## Purpose
Provides shared utilities for namespace summary CLI commands, including Recon HTTP calls, path parsing, and text formatting helpers.

## Important APIs, Types, And Functions
`makeHttpCall` overloads append query parameters, open a `URLConnectionFactory` connection with optional SPNEGO, handle HTTP OK/CREATED, and return response text. Formatting helpers print spaces, newlines, empty/path-not-found/type-not-applicable messages, key-value separators, and underlined headings. `parseInputPath` strips `ofs://authority` to the path component.

## Control Flow
HTTP calls append `?path=...`, optional `files=true` and `replica=true`, print the target URL, connect, read the input stream for successful status, print initialization or unexpected payload messages for other statuses, and handle connection refused/authentication exceptions by returning null.

## State And Persistence
Stateless. It performs network reads from Recon and writes user-facing output.

## Dependencies And Integration Points
Depends on HDFS `URLConnectionFactory`, Ozone configuration, Java `HttpURLConnection`, Apache Commons IO, picocli ANSI, and Recon REST APIs.

## Risks And Test Signals
The path and query parameters are not URL-encoded, and `getInputStream()` is called before checking non-success error streams, which may throw for HTTP errors. Tests should cover URL encoding-sensitive paths, SPNEGO flag, HTTP error responses, connection refused, auth failure, OFS path parsing, and formatting helpers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/NSSummaryCLIUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/QuotaUsageSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/QuotaUsageSubCommand.java

## Purpose
Implements `ozone admin namespace quota`, querying Recon for quota usage of a volume or bucket path.

## Important APIs, Types, And Functions
The command accepts a path, calls `/api/v1/namespace/quota`, parses `allowed` and `used`, and prints allowed, used, and remaining values with `FileUtils.byteCountToDisplaySize`.

## Control Flow
It rejects empty path, builds the Recon URL, calls Recon, handles null response, `PATH_NOT_FOUND`, and `TYPE_NOT_APPLICABLE`, then prints quota fields. `allowed == -1` is displayed as quota not set and remaining unknown.

## State And Persistence
Read-only against Recon namespace/quota summary state.

## Dependencies And Integration Points
Depends on `NSSummaryAdmin`, `NSSummaryCLIUtils`, Recon REST, `JsonUtils`, and `FileUtils`.

## Risks And Test Signals
It does not use `parseInputPath`, so OFS paths may be inconsistent with summary/du. It assumes `allowed` and `used` fields exist for applicable responses. Tests should cover unset quota, over-quota remaining calculation, type-not-applicable, path-not-found, and OFS path input.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/QuotaUsageSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/SummarySubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/SummarySubCommand.java

## Purpose
Implements `ozone admin namespace summary`, querying Recon for entity type and object counts under a namespace path.

## Important APIs, Types, And Functions
The command accepts a path, calls `/api/v1/namespace/summary` through `makeHttpCall`, parses response JSON with `JsonUtils`, and prints entity type plus count stats for volumes, buckets, directories, and keys when present.

## Control Flow
It rejects empty path, parses OFS input paths, calls Recon, handles null response and `PATH_NOT_FOUND`, then reads `countStats` and prints any count whose value is not `-1`.

## State And Persistence
Read-only against Recon namespace summary state.

## Dependencies And Integration Points
Depends on `NSSummaryAdmin`, `NSSummaryCLIUtils`, Recon REST, and Jackson `JsonNode`.

## Risks And Test Signals
It prints `summaryResponse.get("type")` directly, including JSON quoting for strings. Tests should cover all entity types, missing count fields, path-not-found, root/OFS paths, and null responses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/SummarySubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/package-info.java

## Purpose
Documents the Ozone namespace admin CLI package.

## Important APIs, Types, And Functions
No executable APIs are present; the package comment identifies namespace CLI tools.

## Control Flow
No control flow exists.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Javadoc-only integration for Recon namespace summary admin commands.

## Risks And Test Signals
Documentation drift only; compile/Javadoc generation is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/nssummary/package-info.java -->
