# subset-b-008051 Research

Grouped source-tree-aligned research for the requested Ozone CLI admin subset. Each section preserves the source path in the title and is delimited for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/CancelPrepareSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/CancelPrepareSubCommand.java

Purpose: Implements `ozone admin om cancelprepare`, the administrative escape hatch that clears OM prepare mode after upgrade or downgrade preparation. It is intentionally narrow: resolve an OM HA client from an optional service ID, call `OzoneManagerProtocol.cancelOzoneManagerPrepare()`, and print that write requests can resume.

Important APIs and types: Picocli `@Command` and `@Mixin`, `Callable<Void>`, `OmAddressOptions.OptionalServiceIdMixin`, and `OzoneManagerProtocol`. The command's only behavioral method is `call()`.

Control flow: Picocli populates the OM address mixin. `call()` opens an OM protocol client with try-with-resources, invokes `cancelOzoneManagerPrepare`, prints a success message, closes the client, and returns null. Exceptions are not caught locally, so RPC or configuration failures propagate to the CLI framework.

State and persistence behavior: No local state is persisted. The durable effect is remote OM cluster state: the prepare gate is cancelled so OMs can accept writes again. Runtime state is limited to the client proxy.

Dependencies and integration points: Registered under `OMAdmin`; depends on OM address resolution, Hadoop/Ozone admin root configuration and user, and OM protocol server support for prepare cancellation.

Risks: A misresolved service ID or ambiguous HA configuration can target the wrong OM service or fail before RPC. There is no confirmation prompt or status check after cancellation; success is inferred from the RPC returning.

Test signals: Useful tests mock `OzoneManagerProtocol`, verify `cancelOzoneManagerPrepare()` is called once, check success text, and cover optional service ID resolution and propagated RPC failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/CancelPrepareSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/DecommissionOMSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/DecommissionOMSubcommand.java

Purpose: Implements OM HA member decommissioning. It validates the requested OM node ID and host address against configuration, optionally verifies all active OMs have reloaded decommission configuration, then asks the current OM leader to remove the node.

Important APIs and types: `OMAdminProtocolClientSideImpl`, `OzoneConfiguration`, `UserGroupInformation`, `OMNodeDetails`, `OMConfiguration`, `OmUtils`, `ConfUtils`, `OZONE_OM_ADDRESS_KEY`, `OZONE_OM_DECOMMISSIONED_NODES_KEY`, and nested `NodeIdOptions`/`HostnameOptions` with deprecated hidden aliases.

Control flow: `call()` obtains root configuration and user from `OMAdmin`, runs `verifyNodeIdAndHostAddress()`, and unless `--force` is set runs `verifyConfigUpdatedOnAllOMs()`. It then creates an HA admin proxy for the service ID, builds an `OMNodeDetails` for the target, invokes `decommission`, and prints success or failure before rethrowing errors.

State and persistence behavior: Local state stores the resolved target `InetAddress`, configuration, and user for the command invocation only. Persistent state is remote: OM Ratis membership and certificate/store metadata may be updated by the server. The config verification reads local and remote reloaded config but does not edit files.

Dependencies and integration points: Integrates Picocli arg groups, HA OM configuration naming, DNS resolution, OM admin protocol proxies for single OM and OM HA leader paths, and decommissioned-node config rollout. It is registered below `OMAdmin`.

Risks: DNS resolution and address equality are strict; host aliases can fail validation. The `--force` path skips a safety check and can decommission before every OM has reloaded config. The command prevents decommissioning the only active OM but cannot by itself preserve quorum in all operator workflows.

Test signals: Cover matching and mismatching node ID/host config, missing config keys, stale remote OM configs, `--force` bypass, deprecated `-nodeid` and `-hostname` options, success output, and IOException propagation from leader decommission.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/DecommissionOMSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FetchKeySubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FetchKeySubCommand.java

Purpose: Implements `ozone admin om fetch-key`, forcing OM to refetch the latest secret key from SCM and reporting the current key UUID.

Important APIs and types: `OmAddressOptions.OptionalServiceIdMixin`, `OzoneManagerProtocol.refetchSecretKey()`, `UUID`, Picocli command metadata, and `Callable<Void>`.

Control flow: The command opens an OM protocol client for the optional service ID, calls `refetchSecretKey`, prints `Current Secret Key ID: <uuid>`, and closes the client.

State and persistence behavior: No local persistence. Remote OM key-manager state may be refreshed from SCM; the returned UUID is only printed.

Dependencies and integration points: Depends on OM-to-SCM secret-key infrastructure and OM protocol support. It is exposed as an `OMAdmin` subcommand.

Risks: It assumes the OM can contact SCM and the caller is authorized. There is no retry or distinction between no-op and newly fetched key beyond the returned UUID.

Test signals: Mock the OM protocol return UUID, verify output formatting, and exercise RPC error propagation and optional service-ID routing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FetchKeySubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FinalizationStatusSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FinalizationStatusSubCommand.java

Purpose: Implements OM upgrade finalization status querying. It asks the selected OM for current finalization progress without starting or taking over finalization and prints only the status enum.

Important APIs and types: `OzoneManagerProtocol.queryUpgradeFinalizationProgress`, `UpgradeFinalization.StatusAndMessages`, UUID-generated upgrade client IDs, and `OmAddressOptions.OptionalServiceIdOrHostMixin`.

Control flow: `call()` creates a unique `Upgrade-Client-<uuid>` ID, opens an OM client from service ID or host, invokes `queryUpgradeFinalizationProgress(upgradeClientID, false, true)`, prints `progress.status()`, and closes the client.

State and persistence behavior: No local persistence. It reads remote finalization state and does not request takeover. The random client ID avoids colliding with real finalization clients.

Dependencies and integration points: Used under `ozone admin om finalizationstatus`; shares address resolution with host-aware OM commands and relies on `UpgradeFinalization` protocol semantics.

Risks: Printing only the enum omits progress messages, so operators needing details must use finalize/monitor flows. Wrong host/service selection can report a different OM view.

Test signals: Verify the progress query flags, random client prefix shape, status output, host/service option parsing, and exception propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FinalizationStatusSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FinalizeUpgradeSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FinalizeUpgradeSubCommand.java

Purpose: Starts and monitors OM metadata upgrade finalization. It handles already-finalized responses, invalid start responses, takeover of an existing monitor, and streaming finalization progress messages until completion.

Important APIs and types: `OzoneManagerProtocol.finalizeUpgrade`, `queryUpgradeFinalizationProgress`, `UpgradeFinalization` status helpers and emitters, `UpgradeException`, `ExecutorService`, `Future`, `CancellationException`, and `OmAddressOptions.OptionalServiceIdOrHostMixin`.

Control flow: `call()` creates an upgrade client ID, opens an OM client, and calls `finalizeUpgrade`. If the response is already finalized it prints and exits. If it is not a starting state, it reports an invalid response and throws. Otherwise `monitorAndWaitFinalization()` submits `UpgradeMonitor` to a single-thread executor. The monitor polls every 500 ms, prints ordered progress messages for in-progress or done states, exits on done, and handles the already-finalized takeover edge case.

State and persistence behavior: The command persists nothing locally. The server-side finalization changes OM metadata layout and enables finalized features. Runtime state is the generated client ID, `--takeover` flag, and monitor thread lifecycle.

Dependencies and integration points: Integrated under `OMAdmin`; shares status wording and error handling with `UpgradeFinalization` utility code. It depends on OM protocol finalization RPCs and host/service address selection.

Risks: The monitor loops indefinitely until the server reports done or an exception occurs. Interrupted monitoring emits cancellation but remote finalization may continue. `--takeover` changes ownership semantics for an in-flight request and must match server behavior.

Test signals: Mock responses for finalized, starting, invalid, in-progress, done, takeover, cancellation, interruption, and execution exception; assert emitted messages, executor shutdown, and `UpgradeException` handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FinalizeUpgradeSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/GetServiceRolesSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/GetServiceRolesSubcommand.java

Purpose: Lists OM service members and their Ratis roles in plain text, JSON, or table form.

Important APIs and types: `OzoneManagerProtocol.getServiceList()`, `ServiceInfo`, `OMRoleInfo`, `HddsProtos.NodeType.OM`, `JsonUtils`, `FormattingCLIUtils`, and Picocli `--json`/`--table` options.

Control flow: `call()` opens an OM client. JSON output maps each OM node ID to `serverRole` and `hostname`; table output adds rows under `Host Name`, `Node ID`, and `Role`; default output prints `nodeId : role (hostname)`. Non-OM service entries and entries with null OM role info are skipped.

State and persistence behavior: Read-only. It formats a service-list snapshot returned by OM and does not mutate local or remote state.

Dependencies and integration points: Registered as `roles` with alias `getserviceroles`; depends on OM service discovery and Ratis role reporting.

Risks: `--json` and `--table` are independent booleans; JSON wins if both are set. The JSON shape is a list of single-entry maps, which clients may depend on even though it is awkward for lookup.

Test signals: Verify filtering of non-OM entries, all three output formats, option precedence, empty lists, and stable table headers/JSON keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/GetServiceRolesSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/ListOpenFilesSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/ListOpenFilesSubCommand.java

Purpose: Lists open OM keys/files, with paging, path-prefix filtering, optional JSON output, and optional inclusion of hsync-deleted or hsync-overwritten open-key records.

Important APIs and types: `OzoneManagerProtocol.getServiceInfo()`, `RpcClient.getOmVersion`, `OzoneManagerVersion.HBASE_SUPPORT`, `listOpenFiles`, `ListOpenFilesResult`, `OpenKeySession`, `OmKeyInfo`, `OzoneConsts` hsync metadata keys, `JsonUtils`, and `OmAddressOptions.OptionalServiceIdOrHostMixin`.

Control flow: `call()` opens an OM client and delegates to `execute`. The command rejects old OM versions by printing an error and returning. It calls `listOpenFiles(pathPrefix, limit, startItem)`, removes deleted or overwritten hsync records unless requested, and then prints either full JSON or a human table-like listing. Human output includes total count, shown count, path prefix, optional continuation token, client ID, creation time, hsync/deleted/overwritten columns, full key path, and a next-batch command if `hasMore()` is true.

State and persistence behavior: Read-only local behavior. It mutates the returned `ListOpenFilesResult.getOpenKeys()` list in memory when filtering. Continuation state is represented by the server-returned token and printed command, not stored.

Dependencies and integration points: Uses OM protocol list-open-files support, OM version gating for HBase support, Ozone key metadata conventions, and OM address `toString()` to reconstruct a follow-up CLI command.

Risks: Filtering mutates the response object before JSON output, so JSON respects CLI filters rather than server raw output. `HSYNC_CLIENT_ID` is parsed as a long only when `isHsync()` is true; malformed metadata can fail output. The next-batch command does not shell-quote path prefixes or start tokens.

Test signals: Cover version-gate errors, deleted/overwritten filtering, hsync client ID display, JSON vs human output, continuation command generation, limit/prefix/start parsing, and full path formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/ListOpenFilesSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/OMAdmin.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/OMAdmin.java

Purpose: Root Picocli subcommand for Ozone Manager administration and factory for OM protocol clients used by child commands.

Important APIs and types: `AdminSubcommand`, `@MetaInfServices`, `OzoneAdmin`, `OzoneManagerProtocolClientSideTranslatorPB`, `OzoneManagerProtocolPB`, `Hadoop3OmTransportFactory`, `OmTransport`, `OzoneConfiguration`, `UserGroupInformation`, `OZONE_OM_ADDRESS_KEY`, `OZONE_OM_SERVICE_IDS_KEY`, and `ClientId`.

Control flow: Picocli registers OM subcommands for finalization, list-open-files, roles, prepare/cancelprepare, decommission, Ranger sync, leader transfer, key fetch, lease, and snapshot operations. `createOmClient` sets a direct OM host if supplied, otherwise resolves a service ID or requires exactly one configured service ID. It configures the protobuf RPC engine, creates an OM transport, and returns a client translator. With `forceHA`, a non-HA service ID causes an `OzoneClientException`.

State and persistence behavior: It does not persist state. It can mutate the passed `OzoneConfiguration` by setting `ozone.om.address` when a host is provided. Runtime state includes the parent `OzoneAdmin`.

Dependencies and integration points: Service-provider registration makes `om` available to `ozone admin`. All OM child commands depend on this class for parent config/user and client creation.

Risks: Host mode intentionally nulls service ID and mutates config. Ambiguous zero-or-many service IDs without explicit service ID throw. The force-HA branch is used by HA-only commands and can reject otherwise valid host-mode usage.

Test signals: Validate subcommand registration, direct-host override, single service ID inference, ambiguity failure, forceHA rejection, and RPC engine/transport creation paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/OMAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/OmAddressOptions.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/OmAddressOptions.java

Purpose: Provides reusable Picocli mixins for commands that need an OM service ID, OM host, or either. It centralizes option names, deprecated aliases, client creation, and address string rendering.

Important APIs and types: `AbstractMixin`, `rootCommand().getUser()`, `OMAdmin.createOmClient`, nested `OptionalServiceIdMixin`, `MandatoryServiceIdMixin`, `OptionalServiceIdOrHostMixin`, `MandatoryServiceIdOrHostMixin`, `ServiceIdOptions`, and `ServiceIdAndHostOptions`.

Control flow: Service-only mixins call `createOmClient(conf, user, serviceID, null, true)` and require HA-compatible service resolution. Service-or-host mixins call `createOmClient(conf, user, serviceID, host, false)`. Arg groups enforce optional or mandatory presence. Deprecated `-id` and `-host` values are returned if the modern options are absent.

State and persistence behavior: No persistence. Option objects store parsed values for the current invocation. `toString()` renders options back into CLI fragments, used by list-open-files pagination.

Dependencies and integration points: Used by most OM admin subcommands and indirectly by generated next-batch command text. It is coupled to root-command user/config access through `AbstractMixin`.

Risks: `ServiceIdAndHostOptions` extends `ServiceIdOptions`, so rendering can produce both service ID and host when supplied through aliases; host mode later overrides service ID in `OMAdmin`. The rendered option string is not shell-escaped.

Test signals: Exercise optional and mandatory multiplicity, modern and deprecated options, host/service precedence, `newClient()` forceHA flags, and `toString()` output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/OmAddressOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/PrepareSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/PrepareSubCommand.java

Purpose: Prepares all OMs in an HA service for upgrade or downgrade by asking OM to apply pending transactions, snapshot at a quorum transaction, purge logs, and then polling individual OMs until a majority or all complete.

Important APIs and types: `OzoneManagerProtocol.prepareOzoneManager`, `getOzoneManagerPrepareStatus`, `PrepareStatusResponse`, `PREPARE_COMPLETED`, `OmUtils.getOmHostsFromConfig`, `OMAdmin.createOmClient`, `Time.monotonicNow`, duration options, and deprecated hidden timing aliases.

Control flow: `execute()` calls `prepareOzoneManager(waitTimeout, checkInterval)` and prints the returned transaction ID. It builds a map of configured OM hosts to unprepared, then loops until timeout or all hosts prepare. Each iteration opens a single-OM client, queries status for the prepare transaction, logs status and transaction index, records completed hosts, catches per-host IOExceptions, and sleeps between rounds. After the loop it throws if fewer than a majority prepared; otherwise it prints success and any remaining unprepared hosts.

State and persistence behavior: Local state is the host-prepared map and timing values. Remote durable state is the OM prepare barrier, Ratis snapshot/log purge, and write rejection until cancellation or finalization. Deprecated option values are resolved only for the invocation.

Dependencies and integration points: Requires an explicit OM service ID; uses parent OM admin to create per-host clients and Ozone configuration to enumerate hosts.

Risks: Majority success can leave minority OMs unprepared, which is reported but still exits successfully. Per-host IOExceptions are swallowed during polling until majority logic fails. Hidden timing options and deprecated aliases can make tests brittle if defaults change.

Test signals: Mock transaction ID, per-host completed/in-progress/error status, majority vs minority completion, timeout behavior, deprecated timing option resolution, and emitted waiting/success/failure messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/PrepareSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/TransferOmLeaderSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/TransferOmLeaderSubCommand.java

Purpose: Manually transfers OM Ratis leadership either to a named OM node ID or to a randomly selected follower.

Important APIs and types: `OzoneManagerProtocol.transferLeadership`, `OmAddressOptions.OptionalServiceIdMixin`, Picocli `ArgGroup`, and nested `TransferOption` with `--new-leader-id` aliases and `--random`.

Control flow: Picocli enforces exactly one transfer mode. `call()` converts random mode to an empty target string, opens an OM client, invokes `transferLeadership`, and prints whether transfer went to a random node or the specified node.

State and persistence behavior: No local persistence. The remote Ratis group leader changes if the server accepts the request.

Dependencies and integration points: Used under `OMAdmin`; relies on OM service ID resolution and OM-side leadership transfer semantics where empty string means random follower.

Risks: The empty-string sentinel is a protocol convention and must stay aligned with OM server logic. There is no post-transfer verification that the target became leader.

Test signals: Verify arg-group exclusivity, random sentinel, explicit node ID, RPC invocation, and success text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/TransferOmLeaderSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/UpdateRangerSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/UpdateRangerSubcommand.java

Purpose: Triggers the OM leader's Ranger background sync task to push policy and role updates to Ranger, optionally without waiting for completion.

Important APIs and types: `OzoneManagerProtocol.triggerRangerBGSync(boolean)`, `OmAddressOptions.OptionalServiceIdOrHostMixin`, `--no-wait`, and Picocli command metadata.

Control flow: The command opens an OM client, invokes `triggerRangerBGSync(noWait)`, prints success on true, and prints an error message to stderr on false. RPC exceptions propagate.

State and persistence behavior: No local state. Remote side may enqueue or run Ranger sync work and update Ranger-side policies/roles depending on OM implementation and authorization.

Dependencies and integration points: Depends on OM admin privilege, Ranger integration, and host/service OM address resolution.

Risks: A false result produces stderr but no exception, so exit-code behavior may still be success. With `--no-wait`, the command can return before the background task result is known.

Test signals: Mock true/false returns, verify stdout/stderr split, no-wait flag propagation, and RPC failure handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/UpdateRangerSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/LeaseRecoverer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/LeaseRecoverer.java

Purpose: Implements `ozone admin om lease recover --path=<path>`, recovering the filesystem lease for an Ozone file path through Hadoop `FileSystem` APIs.

Important APIs and types: `FileSystem.get(URI, OzoneConfiguration)`, `LeaseRecoverable`, `Path`, `URI`, Picocli `CommandSpec`, and required `--path` option.

Control flow: `call()` creates a fresh `OzoneConfiguration`, parses the path as a URI, obtains the corresponding `FileSystem`, checks it implements `LeaseRecoverable`, calls `recoverLease(new Path(uri))`, closes the filesystem, and prints success. Unsupported filesystems throw `IllegalArgumentException`.

State and persistence behavior: No local persistence. The remote filesystem/OM lease state is changed by `recoverLease`; whether blocks are closed or client leases are released is delegated to the filesystem implementation.

Dependencies and integration points: Registered below `LeaseSubCommand`; works with `ofs://` or other configured schemes and Hadoop filesystem resolution.

Risks: The command does not use the root admin configuration directly; it constructs a new configuration. It does not check the boolean result because `LeaseRecoverable.recoverLease` here is invoked for side effects. Unsupported schemes fail after opening a filesystem.

Test signals: Exercise OFS/Ozone filesystem lease recovery, unsupported filesystem error, URI parsing, required path option, and success output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/LeaseRecoverer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/LeaseSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/LeaseSubCommand.java

Purpose: Picocli grouping command for OM lease operations. Its current role is to expose the `recover` subcommand.

Important APIs and types: Picocli `@Command`, `LeaseRecoverer`, and command metadata.

Control flow: The class has no methods; Picocli routes `ozone admin om lease recover` to `LeaseRecoverer`.

State and persistence behavior: No state or persistence in the grouping class.

Dependencies and integration points: Registered in `OMAdmin` and provides the namespace for future lease admin subcommands.

Risks: As a passive grouping class, behavior depends entirely on Picocli registration and child command implementations.

Test signals: CLI help/subcommand discovery should include `recover`, and routing should instantiate `LeaseRecoverer` for recover invocations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/LeaseSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/package-info.java

Purpose: Package documentation for OM lease command-line operations.

Important APIs and types: Declares package `org.apache.hadoop.ozone.admin.om.lease`; no runtime classes or methods are defined here.

Control flow: None. Javadoc associates the package with command-line lease operations.

State and persistence behavior: No state, persistence, or executable behavior.

Dependencies and integration points: Documents the package containing `LeaseSubCommand` and `LeaseRecoverer`.

Risks: Only documentation drift if package purpose changes without updating this file.

Test signals: Not directly tested except through package compilation and Javadoc checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/lease/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/package-info.java

Purpose: Package documentation for Ozone Manager admin CLI tools.

Important APIs and types: Declares package `org.apache.hadoop.ozone.admin.om`; no executable APIs.

Control flow: None.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Documents the OM admin command package used by `OMAdmin` and its subcommands.

Risks: Documentation text is minimal and can become stale as the package grows.

Test signals: Compilation/Javadoc validation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/DefragSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/DefragSubCommand.java

Purpose: Triggers the OM snapshot defragmentation service on a selected OM node, with optional asynchronous no-wait behavior.

Important APIs and types: `AbstractSubcommand`, `OmAddressOptions.OptionalServiceIdMixin`, `OMNodeDetails.getOMNodeDetailsFromConf`, `OMAdminProtocolClientSideImpl.createProxyForSingleOM`, `UserGroupInformation`, `triggerSnapshotDefrag(boolean)`, `--node-id`, and `--no-wait`.

Control flow: `call()` resolves OM node details from configuration, service ID, and optional node ID. If resolution fails it prints an error and returns. Otherwise it creates a single-OM admin proxy and calls `execute`. `execute` prints a trigger message, invokes `triggerSnapshotDefrag(noWait)`, and prints background-triggered, completed, or failed/interrupted messaging based on `noWait` and the boolean result.

State and persistence behavior: No local persistence. Remote OM snapshot DB/files may be compacted or defragmented by the service. The command's boolean result is the only observed completion state.

Dependencies and integration points: Registered below `SnapshotSubCommand`; requires HA OM configuration and single-OM admin protocol access.

Risks: If `--node-id` is omitted in multi-OM configs, resolution semantics are delegated to `OMNodeDetails`. A false result only prints failure text and does not throw. `--no-wait` reports successful trigger without knowing final service outcome.

Test signals: Mock node-detail resolution, client creation, true/false/no-wait outcomes, IOException propagation and stderr message, and HA config failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/DefragSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/SnapshotSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/SnapshotSubCommand.java

Purpose: Picocli grouping command for OM snapshot-related admin operations. Currently it exposes snapshot defragmentation.

Important APIs and types: Picocli `@Command` and `DefragSubCommand`.

Control flow: No methods. Picocli routes `ozone admin om snapshot defrag` to the child command.

State and persistence behavior: No state or persistence in the grouping class.

Dependencies and integration points: Registered as a child of `OMAdmin` and names the snapshot admin namespace.

Risks: Passive registration only; missing child registration would hide snapshot operations.

Test signals: CLI command discovery/help should include `defrag` under `om snapshot`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/SnapshotSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/package-info.java

Purpose: Package documentation for Ozone Manager snapshot command-line operations.

Important APIs and types: Declares package `org.apache.hadoop.ozone.admin.om.snapshot`.

Control flow: None.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Documents the package containing snapshot admin commands.

Risks: Documentation drift only.

Test signals: Compilation/Javadoc validation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/package-info.java

Purpose: Package documentation for top-level Ozone admin CLI tools.

Important APIs and types: Declares package `org.apache.hadoop.ozone.admin`; no executable APIs.

Control flow: None.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Documents the namespace containing `OzoneAdmin` and admin subcommand providers such as OM and SCM.

Risks: The text mentions SCM and Ozone admin tools broadly; it should be kept aligned with package responsibilities.

Test signals: Compilation/Javadoc validation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/AbstractReconfigureSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/AbstractReconfigureSubCommand.java

Purpose: Shared base for `ozone admin reconfig` action commands. It decides whether to target one node address or all in-service datanodes, then dispatches the concrete operation.

Important APIs and types: `Callable<Void>`, parent `ReconfigureCommands`, `ExecutorService`, `Executors.newFixedThreadPool(5)`, `ReconfigureSubCommandUtil.parallelExecute`, and abstract `executeCommand(NodeType, String)`.

Control flow: `call()` checks `parent.isBatchReconfigDatanodes()`. Batch mode gets all operable datanode client RPC addresses and runs the concrete operation in parallel. Single-node mode requires `--address`, prints an error and returns if missing, otherwise calls `executeCommand(parent.getService(), parent.getAddress())`.

State and persistence behavior: No persistence. Runtime state is inherited parent options and a batch executor. Remote reconfiguration state is changed only by subclasses.

Dependencies and integration points: Base class for start, status, and properties subcommands. Depends on the parent command for service/address/batch selection.

Risks: Batch mode always uses datanode node type in the utility, regardless of the parent `--service` value. Missing address prints an error without non-zero exception. The executor size and timeout are fixed in utility code.

Test signals: Cover missing address, single OM/SCM/DATANODE dispatch, batch datanode address collection, and exception behavior from subclass operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/AbstractReconfigureSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureCommands.java

Purpose: Root command for dynamic server reconfiguration. It defines common options and registers `start`, `status`, and `properties` subcommands.

Important APIs and types: `AdminSubcommand`, `@MetaInfServices`, `OzoneAdmin`, `ContainerOperationClient`, `ScmClient`, `HddsProtos.NodeType`, `--service`, `--address`, and `--in-service-datanodes`.

Control flow: Picocli parses service/address/batch options. `getService()` converts the service string with `NodeType.valueOf`. `getAllOperableNodesClientRpcAddress()` opens a `ContainerOperationClient`, asks `ReconfigureSubCommandUtil` for IN_SERVICE datanode addresses, wraps IOExceptions in RuntimeException, and closes the client.

State and persistence behavior: Holds parsed CLI options for a command invocation only. No local persistence.

Dependencies and integration points: Registered as an admin subcommand provider. It bridges the generic Ozone admin root configuration to SCM node discovery for datanode batch reconfiguration.

Risks: `NodeType.valueOf` is case-sensitive and can throw for lowercase service values. Batch mode can be selected with a non-DATANODE service, while the base class still executes datanode operations.

Test signals: Command registration, service parsing, address requirement via base class, SCM client closure, batch query failure wrapping, and valid/invalid service strings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigurePropertiesSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigurePropertiesSubcommand.java

Purpose: Lists reconfigurable properties for a selected OM, SCM, datanode, or batch of in-service datanodes.

Important APIs and types: `ReconfigureProtocol.getServerName()`, `listReconfigureProperties()`, `ReconfigureSubCommandUtil.getSingleNodeReconfigureProxy`, `HddsProtos.NodeType`, and inherited dispatch from `AbstractReconfigureSubCommand`.

Control flow: For each target, `executeCommand` opens a reconfigure proxy, obtains the server name and property list, prints a header with node address, then prints one property per line. IOExceptions print an address-specific error and are rethrown as RuntimeException.

State and persistence behavior: Read-only. No remote reconfiguration starts; it reads server-declared property metadata.

Dependencies and integration points: Shares proxy creation with reconfig start/status; used for both single-node and batch datanode modes.

Risks: Unlike start/status, this command wraps IOExceptions in RuntimeException, which can affect batch success/failure accounting differently. Output is plain text only.

Test signals: Mock property lists, empty lists, IOException wrapping, server-name header, and batch per-node output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigurePropertiesSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureStartSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureStartSubcommand.java

Purpose: Starts an asynchronous reconfiguration task on selected server nodes.

Important APIs and types: `ReconfigureProtocol.startReconfigure()`, `getServerName()`, `ReconfigureSubCommandUtil.getSingleNodeReconfigureProxy`, and inherited target dispatch.

Control flow: `executeCommand` opens the proxy, gets the server name, calls `startReconfigure`, and prints a started message. IOExceptions are caught, an address-specific message and stack trace are printed to stdout, and no exception is rethrown.

State and persistence behavior: No local persistence. Remote servers may start background reconfiguration tasks that later modify runtime configuration values.

Dependencies and integration points: Works for OM, SCM, and DATANODE single-node modes and datanode batch mode through the base command.

Risks: Because IOException is swallowed after printing, callers may see a zero exit for single-node failures. Batch utility may also count such handled failures as successful because no exception escapes.

Test signals: Verify start RPC, server-name output, IOException stack trace output, proxy closure, and batch counting behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureStartSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureStatusSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureStatusSubcommand.java

Purpose: Prints the current or last reconfiguration task status for selected nodes, including per-property success and failure details after completion.

Important APIs and types: `ReconfigureProtocol.getReconfigureStatus()`, `ReconfigurationTaskStatus`, `ReconfigurationUtil.PropertyChange`, `Optional<String>` error values, `Date`, and inherited target dispatch.

Control flow: `executeCommand` opens a proxy, reads server name and task status, prints a node prefix, and delegates to `printReconfigurationStatus`. Status printing handles no task, running task, stopped task with no property status, and stopped task with per-property results. Success is represented by absent error optional; failure prints the error text.

State and persistence behavior: Read-only from the CLI side. It observes server-side reconfiguration task timestamps and result maps.

Dependencies and integration points: Uses Hadoop common reconfiguration status types and the Ozone reconfigure protocol translator.

Risks: IOExceptions are printed with stack traces but not rethrown, similar to start. Date formatting uses default JVM timezone/locale. Output is plain text and may be parsed by scripts.

Test signals: No-task, running, completed success/failure map, null status map, IOException handling, and batch output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureStatusSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureSubCommandUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureSubCommandUtil.java

Purpose: Utility methods for reconfiguration command proxy creation, bounded parallel execution, and discovery of live in-service datanode client RPC addresses.

Important APIs and types: `ReconfigureProtocolClientSideTranslatorPB`, `NetUtils.createSocketAddr`, `UserGroupInformation`, `OzoneConfiguration`, `ExecutorService`, `AtomicInteger`, `ScmClient.queryNode`, `DatanodeDetails`, `Port.Name.CLIENT_RPC`, `NodeOperationalState.IN_SERVICE`, and `HddsProtos.NodeState.DEAD`.

Control flow: `getSingleNodeReconfigureProxy` builds a new configuration, current user, socket address, and protocol translator. `parallelExecute` submits one task per node, calls the supplied operation with `NodeType.DATANODE`, counts successes/failures, waits up to three minutes, and prints summary counts. `getAllOperableNodesClientRpcAddress` queries SCM for IN_SERVICE nodes, skips DEAD nodes, extracts CLIENT_RPC ports, and logs missing ports.

State and persistence behavior: No persistence. Runtime counters track batch results; remote state is changed only by the supplied operation.

Dependencies and integration points: Central dependency for all reconfig subcommands and the parent command's datanode batch mode.

Risks: `parallelExecute` hardcodes `DATANODE` node type and only waits three minutes total. It does not throw on timeout. Missing client RPC ports only print a message. It creates a new default `OzoneConfiguration` for single-node proxy creation rather than using root command config.

Test signals: Proxy address parsing, batch success/failure counting, timeout/interruption behavior, skipping DEAD nodes, missing CLIENT_RPC handling, and address formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/ReconfigureSubCommandUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/package-info.java

Purpose: Package documentation for reconfiguration-related admin tools.

Important APIs and types: Declares package `org.apache.hadoop.ozone.admin.reconfig`.

Control flow: None.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Documents the package containing dynamic reconfiguration CLI commands.

Risks: Documentation drift only.

Test signals: Compilation/Javadoc validation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/reconfig/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/DecommissionScmSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/DecommissionScmSubcommand.java

Purpose: Implements `ozone admin scm decommission`, removing an SCM from the SCM Ratis ring and certificate store through `ScmClient`.

Important APIs and types: `ScmSubcommand`, `ScmClient.decommissionScm`, `DecommissionScmResponseProto`, nested `NodeIdOptions`, and deprecated hidden `-nodeid` alias.

Control flow: `execute()` calls `decommissionScm(nodeId)`. If the response success flag is false, it builds an error message including optional server error text and throws IOException for a non-zero exit. On success it prints `Decommissioned Scm <nodeId>`.

State and persistence behavior: No local persistence. Remote SCM membership/certificate state changes on success.

Dependencies and integration points: Registered below `ScmAdmin`; uses the standard `ScmSubcommand` client lifecycle.

Risks: It trusts the response success flag and optional error message. There is no config preflight comparable to OM decommissioning.

Test signals: Success/failure response handling, error message inclusion, deprecated alias parsing, and exception exit behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/DecommissionScmSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/DeletedBlocksTxnCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/DeletedBlocksTxnCommands.java

Purpose: Picocli grouping command for SCM deleted-block transaction operations. It currently exposes the summary subcommand.

Important APIs and types: Picocli `@Command`, `HddsVersionProvider`, and `GetDeletedBlockSummarySubcommand`.

Control flow: No methods; Picocli routes `ozone admin scm deletedBlocksTxn summary` to the child.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Registered under `ScmAdmin` as the namespace for deleted-block transaction admin commands.

Risks: Passive registration only.

Test signals: CLI help and child command routing should include `summary`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/DeletedBlocksTxnCommands.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/FinalizationScmStatusSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/FinalizationScmStatusSubcommand.java

Purpose: Queries SCM upgrade finalization status and prints the current status enum.

Important APIs and types: `ScmSubcommand`, `ScmClient.queryUpgradeFinalizationProgress`, `UpgradeFinalization.StatusAndMessages`, and UUID-generated upgrade client IDs.

Control flow: `execute()` creates a unique client ID, calls `queryUpgradeFinalizationProgress(upgradeClientID, false, true)`, and prints `progress.status()`.

State and persistence behavior: Read-only. It observes remote SCM finalization state and stores nothing locally.

Dependencies and integration points: Registered under `ScmAdmin`; mirrors the OM status command using SCM client APIs.

Risks: Only the enum is printed, not detailed messages. Parent field is unused.

Test signals: Verify query flags, status output, UUID client ID prefix, and IOException propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/FinalizationScmStatusSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/FinalizeScmUpgradeSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/FinalizeScmUpgradeSubcommand.java

Purpose: Starts and monitors SCM upgrade finalization, paralleling the OM finalization command but using `ScmClient`.

Important APIs and types: `ScmClient.finalizeScmUpgrade`, `queryUpgradeFinalizationProgress`, `UpgradeFinalization` helpers/emitters, `StatusAndMessages`, `UpgradeException`, `ExecutorService`, and `Future`.

Control flow: `execute()` creates an upgrade client ID and calls `finalizeScmUpgrade`. Already finalized prints and exits; a non-starting response prints invalid status and throws IOException; `UpgradeException` is passed to shared invalid-request handling with the takeover flag. It then monitors progress in a single-thread executor, polling every 500 ms, printing messages for in-progress/done states, handling already-finalized takeover, and emitting finished/cancel/error messages.

State and persistence behavior: No local persistence. Remote SCM finalization mutates SCM metadata layout and feature finalization state.

Dependencies and integration points: Registered below `ScmAdmin`; shares finalization messaging conventions with OM and Ozone upgrade utilities.

Risks: Monitoring can run indefinitely until server status changes. Execution exceptions are wrapped in IOException. The command continues to monitor after handled `UpgradeException`, relying on shared handler semantics.

Test signals: Start/finalized/invalid response paths, takeover handling, message streaming, exception wrapping, cancellation/interruption, and emitted component name `Storage Container Manager`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/FinalizeScmUpgradeSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/GetDeletedBlockSummarySubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/GetDeletedBlockSummarySubcommand.java

Purpose: Prints aggregate deleted-block transaction statistics from SCM.

Important APIs and types: `ScmClient.getDeletedBlockSummary()`, `HddsProtos.DeletedBlocksTransactionSummary`, and `ScmSubcommand`.

Control flow: `execute()` fetches the summary. Null produces `DeletedBlocksTransaction summary is not available`; otherwise it prints total transaction count, block count, block size, and replicated block size.

State and persistence behavior: Read-only. It reports SCM metadata/metrics about queued or tracked deleted-block transactions.

Dependencies and integration points: Child of `DeletedBlocksTxnCommands`, using the standard SCM client provided by the admin CLI.

Risks: Plain text output has fixed labels that scripts may parse. Null summary is handled as unavailable rather than an error.

Test signals: Null summary output, all numeric fields, and IOException propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/GetDeletedBlockSummarySubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/GetScmRatisRolesSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/GetScmRatisRolesSubcommand.java

Purpose: Lists SCM Ratis roles and peer identity data in raw, table, or JSON form.

Important APIs and types: `ScmClient.getScmRoles()`, `JsonUtils`, `FormattingCLIUtils`, Picocli `--json`/`--table`, and role strings split by colon.

Control flow: `execute()` gets role strings. JSON mode parses each string into a map keyed by hostname with address, optional raft role, ID, and InetAddress. Table mode splits each role string and adds it to a five-column table. Default mode prints raw role strings. Invalid split results print an error to stderr; JSON returns an empty map for invalid input.

State and persistence behavior: Read-only. It formats SCM-reported role strings and stores no state.

Dependencies and integration points: Registered as `ozone admin scm roles`; depends on SCM Ratis role string format.

Risks: The parser assumes colon-separated fields and may mishandle IPv6-style addresses. Table mode warns but still attempts to add invalid rows. `--json` takes precedence over `--table`.

Test signals: Valid five-field roles, two-field no-Ratis roles, invalid responses, JSON/table/default output, and option precedence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/GetScmRatisRolesSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/RotateKeySubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/RotateKeySubCommand.java

Purpose: Forces SCM secret-key rotation, optionally with `--force`.

Important APIs and types: `ScmSubcommand`, `ContainerOperationClient`, `ScmClient.rotateSecretKeys(boolean)`, parent `ScmAdmin`, and root command error printing.

Control flow: Although an SCM client is passed to `execute`, the command opens a new `ContainerOperationClient` from the root Ozone configuration. It calls `rotateSecretKeys(force)`, prints root error and returns on IOException, and prints success only when the returned status is true.

State and persistence behavior: No local persistence. Remote SCM key-manager state changes by generating a new key on success.

Dependencies and integration points: Registered under `ScmAdmin`; depends on SCM security/key rotation support and root configuration.

Risks: The supplied `scmClient` parameter is unused, which complicates tests and lifecycle expectations. IOExceptions are swallowed after printing, possibly preserving a success exit. False status produces no output.

Test signals: Force flag propagation, success output, false no-output behavior, IOException root error printing, and use of root configuration to create a new client.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/RotateKeySubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/ScmAdmin.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/ScmAdmin.java

Purpose: Root Picocli subcommand for Storage Container Manager administration.

Important APIs and types: `AdminSubcommand`, `@MetaInfServices`, parent `OzoneAdmin`, and registered subcommands for roles, finalization, transfer, decommission, key rotation, and deleted-block transaction operations.

Control flow: Picocli wires the `scm` namespace and injects the parent command. `getParent()` exposes root configuration and user access to child commands.

State and persistence behavior: No persistence. Runtime state is just the parent reference.

Dependencies and integration points: Service-provider registration exposes the SCM admin command to the Ozone admin CLI.

Risks: Child command availability depends on this static subcommand list. There is no direct client factory here; most SCM child commands rely on `ScmSubcommand` or their own `ScmOption`.

Test signals: Service-loader registration, help/subcommand listing, and parent injection for children.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/ScmAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/TransferScmLeaderSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/TransferScmLeaderSubCommand.java

Purpose: Manually transfers SCM Ratis leadership to a specified SCM UUID or a random follower.

Important APIs and types: `ScmOption.createScmClient`, `ScmClient.transferLeadership`, parent `ScmAdmin`, Picocli `ArgGroup`, and nested `TransferOption`.

Control flow: `call()` creates an SCM client from root config, converts random mode to an empty SCM ID, invokes `transferLeadership`, and prints a success message naming random or explicit target.

State and persistence behavior: No local persistence. Remote SCM Ratis leadership changes if accepted.

Dependencies and integration points: Uses `ScmOption` instead of `ScmSubcommand`, and is registered below `ScmAdmin`.

Risks: The created client is not wrapped in try-with-resources in this method. Empty-string random sentinel must stay aligned with server semantics. There is no post-transfer verification.

Test signals: Arg-group exclusivity, random/explicit target RPC values, client creation from config, and success output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/TransferScmLeaderSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/package-info.java

Purpose: Package documentation for SCM-related admin CLI tools.

Important APIs and types: Declares package `org.apache.hadoop.ozone.admin.scm`.

Control flow: None.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Documents the package containing `ScmAdmin` and SCM subcommands.

Risks: Documentation drift only.

Test signals: Compilation/Javadoc validation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/cli/TestDeprecatedCliOption.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/cli/TestDeprecatedCliOption.java

Purpose: Regression tests for warnings emitted when deprecated CLI options are used.

Important APIs and types: `ListPipelinesSubcommand`, Picocli `CommandLine`, custom execution strategy, captured `PrintStream` stderr, AssertJ assertions, and deprecated flags `-ffc`/`-fst` vs modern `--filter-by-factor`.

Control flow: Setup redirects stderr to a byte buffer. `createCommandLine` installs a stub execution strategy that returns OK without running real SCM behavior, so the tests focus on parsing/deprecation warnings. Tests execute one deprecated option, multiple deprecated options, and a modern long option.

State and persistence behavior: No persistence. Runtime state is captured stderr and restored system streams.

Dependencies and integration points: Validates shared CLI deprecation handling for Picocli commands in the admin module, using the pipeline list command as a representative command with deprecated hidden aliases.

Risks: Tests are sensitive to exact warning wording and option names. They do not verify exit codes beyond using an OK strategy.

Test signals: Stderr contains `WARNING: -ffc is deprecated, please use --filter-by-factor instead`, contains both warnings for two aliases, and is empty for the modern option.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/cli/TestDeprecatedCliOption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/cert/TestCleanExpiredCertsSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/cert/TestCleanExpiredCertsSubcommand.java

Purpose: Tests the certificate cleanup CLI output when SCM security removes expired certificates.

Important APIs and types: `CleanExpiredCertsSubcommand`, mocked `SCMSecurityProtocol`, `CertificateInfo`, serial number, captured stdout/stderr, Mockito, and AssertJ.

Control flow: Setup mocks the security protocol and redirects output. The test builds a certificate info object, has `removeExpiredCertificates()` return it in a list, runs the command, and asserts the serial/certificate info appears in CLI output.

State and persistence behavior: No real certificate store is mutated; persistence is represented by the mocked security protocol return value.

Dependencies and integration points: Exercises the SCM security admin command's formatting against the protocol contract used to remove expired certs.

Risks: Coverage shown is a positive one-certificate path; empty results, multiple certificates, and protocol failures need separate coverage.

Test signals: Output contains the removed certificate's serial/info and streams are restored after test.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/cert/TestCleanExpiredCertsSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestContainerReportSuppressOptions.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestContainerReportSuppressOptions.java

Purpose: Tests container report suppression and unsuppression flows: showing health counts, suppressing missing containers, listing suppressed/non-suppressed containers, and rejecting invalid argument combinations.

Important APIs and types: `ReportSubcommand`, `ListSubCommand`, mocked `ScmClient`, `ReplicationManagerReport`, `ContainerID`, `ContainerInfo`, `LifeCycleState`, container health states, `suppressContainers`, `listContainer`, Picocli, and captured stdout/stderr.

Control flow: Setup creates a mock SCM client that returns a report with empty/missing counts, list-container results that distinguish suppressed and all entries, and successful suppress/unsuppress calls. Tests parse command args for normal report, `--suppress`, `--unsuppress`, list suppressed, list non-suppressed, and invalid container IDs without suppress flags. Each command is executed directly against the mock.

State and persistence behavior: Persistent SCM suppression state is modeled by mock collections. Test state includes constructed container lists and report objects; no real SCM metadata is changed.

Dependencies and integration points: Covers interaction between report and list container CLI commands and SCM suppression APIs, including the user-visible effect of suppressed missing containers on report counts.

Risks: The test class uses ordered tests and mutable mocked report/list setup, which can hide inter-test coupling. Output assertions mostly check substrings rather than full JSON/table structure.

Test signals: Report shows `EMPTY: 1` and `MISSING: 1`; suppress prints `Suppressed container: 2`; subsequent report shows missing zero; unsuppress restores missing; list outputs include or exclude container IDs and `suppressed` JSON fields; invalid IDs without suppress/unsuppress throw `ParameterException`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestContainerReportSuppressOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestInfoSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestInfoSubCommand.java

Purpose: Tests container info CLI parsing and output for single/multiple container IDs, stdin input, JSON output, replica inclusion, EC replica indexes, and replica-fetch errors.

Important APIs and types: `InfoSubcommand`, mocked `ScmClient`, `ContainerWithPipeline`, `ContainerInfo`, `Pipeline`, `ContainerReplicaInfo`, `ECReplicationConfig`, `RatisReplicationConfig`, `PipelineNotFoundException`, Picocli, Jackson `JsonNode`, and captured output streams.

Control flow: Setup mocks `getContainerWithPipeline` by ID and makes missing pipeline lookup throw. Tests parse args or feed stdin, run `cmd.execute(scmClient)`, then validate human or JSON output. Helpers construct containers, datanode UUIDs, replica sets with optional replica indexes, and validate invalid ID failures.

State and persistence behavior: No persistence; all SCM state is mocked. Runtime state includes captured standard streams and generated datanode/container fixtures.

Dependencies and integration points: Exercises CLI behavior over SCM container info, pipeline and replica retrieval, stdin parsing convention using `-`, and JSON schema emitted by the command.

Risks: Regex-based validation is sensitive to formatting. Replica-fetch errors are expected to omit replicas rather than fail the whole command, which is a behavior contract. Pipeline-not-found is mocked globally and may not cover pipeline-success rendering.

Test signals: Missing parameter exception, invalid ID `ParameterException`, multiple container outputs, stdin and JSON stdin handling, UUID patterns in replica output, sorted replica indexes for EC, absence of replicas on errors, and JSON containing/omitting `replicas` as expected.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestInfoSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestReconcileSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestReconcileSubcommand.java

Purpose: Tests the container reconcile CLI for status and trigger modes across valid containers, mismatched replicas, stdin input, invalid IDs, EC/open container rejection, server-side failures, and authentication stop behavior.

Important APIs and types: `ReconcileSubcommand`, mocked `ScmClient`, `ContainerInfo`, `ContainerReplicaInfo`, `RatisReplicationConfig`, `ECReplicationConfig`, `LifeCycleState`, `AccessControlException`, Picocli `CommandLine`, Jackson JSON parsing, Mockito verification, and captured stdout/stderr.

Control flow: Setup mocks reconciliation RPCs and stream capture. Helpers parse args with `container reconcile`, execute status or trigger modes from args or stdin, create containers and replica sets, and validate JSON status output. Tests cover matching and mismatching data checksums, no input, mixing stdin and args, unsupported EC/open status, invalid reconcile RPCs, mixed valid/invalid batches, auth failure short-circuiting, invalid numeric IDs, and unreachable containers.

State and persistence behavior: No real SCM state. Mocked containers and replicas model SCM metadata; `reconcileContainer` side effects are verified by Mockito. JSON output is transient captured text.

Dependencies and integration points: Exercises command integration with SCM container metadata, replica checksum comparison, stdin convention, root CLI exit handling for auth failures, and error aggregation.

Risks: The command deliberately continues past some per-container failures but stops on authentication failure; tests guard that distinction. JSON validation uses parsed maps with integer casts, so schema changes can break tests. Server-side restrictions are partly mocked because actual validation lives in SCM.

Test signals: JSON arrays with `replicasMatch`, container state/replication fields, replica datanode maps and checksum hex strings, success trigger messages, aggregated failure counts, stderr not mentioning valid containers, auth failure verifies only first RPC, and invalid IDs produce no output for valid-looking IDs in the same batch.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestReconcileSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestReportSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestReportSubCommand.java

Purpose: Tests the container replication manager report CLI for empty reports, JSON output, and populated unhealthy-container samples.

Important APIs and types: `ReportSubcommand`, mocked `ScmClient`, `ReplicationManagerReport`, `ContainerHealthResult.HealthState`, `ContainerID`, `ContainerInfo`, Picocli, regex matchers, and captured stdout/stderr.

Control flow: Tests mock `getReplicationManagerReport()` to return either an empty report or a report populated by `createReport()`. The command is executed with default or `--json` args, and output is matched for report timestamp, health counters, missing/under/over/unhealthy states, and limited container ID lists.

State and persistence behavior: No real persistence. The report object holds in-memory counts and sample unhealthy containers that model SCM replication-manager state.

Dependencies and integration points: Validates CLI formatting for SCM replication manager reports and the JSON branch consumed by operators or tools.

Risks: Regex assertions are formatting-sensitive but do not fully validate JSON semantics. The fixture samples a bounded container list, so truncation behavior is represented by helper-generated ranges.

Test signals: Empty report shows zero counts for all health states, valid JSON begins with expected report fields, populated report shows expected counts and sample container lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/container/TestReportSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestContainerBalancerSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestContainerBalancerSubCommand.java

Purpose: Tests container balancer CLI status, verbose/history output, start, and stop behavior against a mocked SCM client.

Important APIs and types: `ContainerBalancerStatusSubcommand`, `ContainerBalancerStartSubcommand`, `ContainerBalancerStopSubcommand`, `ContainerBalancerStatusInfoResponseProto`, `ContainerBalancerTaskIterationStatusInfo`, `ContainerBalancerConfiguration`, `IterationInfo`, regex patterns for output, Mockito, and AssertJ.

Control flow: Helpers build status response protos with running/stopped state, iteration history, balancing stats, and configuration. Tests execute status without flags, verbose history, verbose current output, stopped balancer status, stop success/failure, start success, and start failure when already running. Output is captured through helper stream suppliers and matched with patterns.

State and persistence behavior: No persistence. Mocked SCM client responses model the balancer's in-memory service status and configuration. Start/stop state changes are represented by mocked RPC returns or thrown IOExceptions.

Dependencies and integration points: Exercises CLI formatting over SCM container balancer service APIs and validates configuration display for balancing thresholds, move limits, data sizes, and duration values.

Risks: Many assertions are regex-based and sensitive to wording. Time/duration formatting must remain stable. Start and stop tests focus on user-visible output rather than verifying every configuration field sent to SCM.

Test signals: `Container Balancer is Running/Not Running`, started-at and duration fields, verbose iteration stats/history, stop waiting message, failed stop stderr, start success text, and failed start exception/message.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestContainerBalancerSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDecommissionStatusSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDecommissionStatusSubCommand.java

Purpose: Tests datanode decommission status output for all nodes and filtered node selection by ID or IP, including success/failure health, metrics, container lists, no-node output, and unsupported hostname filtering.

Important APIs and types: `DecommissionStatusSubCommand`, mocked `ScmClient`, `HddsProtos.Node`, `DatanodeDetails`, `ContainerID`, SCM metrics strings, Picocli, parameterized `--id`/`--node-id`, and captured output streams.

Control flow: Fixtures create two decommissioning node protos, per-node container lists, and metrics strings. Tests mock `queryNode`, `getContainersOnDecomNode`, and `getMetrics`, parse filter options, execute the command, and assert which hostnames, metrics, and container IDs appear. Hostname option test expects a `ParameterException`.

State and persistence behavior: No persistence. Mocked SCM state represents node operational state, pending containers, and decommission metrics.

Dependencies and integration points: Validates the CLI's use of SCM node query and decommission progress APIs and the supported filter contract.

Risks: Metrics are opaque strings from SCM and are asserted by substring. The command rejects hostname filtering despite common operator expectations; the test locks this behavior.

Test signals: Both nodes shown by default, no-node message with no metrics/container lists, ID and IP filters include only matching host, success/failure metrics alter container display, and `--hostname` is rejected.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDecommissionStatusSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDecommissionSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDecommissionSubCommand.java

Purpose: Tests datanode decommission command output and error handling when decommissioning hostnames from args or stdin.

Important APIs and types: `DecommissionSubCommand`, mocked `ScmClient.decommissionNodes`, `DatanodeAdminError`, Picocli, regex output checks, and captured stdout/stderr.

Control flow: Setup redirects streams and prepares the command. Tests feed hostnames through stdin using `-` or positional args, mock empty error results for success, or return per-host errors. The command is executed directly against the mock and output/error behavior is asserted.

State and persistence behavior: No real datanode state changes. Mocked SCM return values represent accepted decommission requests or validation errors.

Dependencies and integration points: Covers CLI parsing and output around SCM datanode admin decommission APIs.

Risks: Success output is accepted after SCM returns no errors, not after decommission completes. Error paths throw IOException after printing per-node errors.

Test signals: Stdin hostnames are all reported, successful decommission messages for host1/host2, error messages include node and cause, and IOException is thrown on reported errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDecommissionSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDiskBalancerSubCommands.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDiskBalancerSubCommands.java

Purpose: Comprehensive unit tests for datanode disk balancer CLI start, stop, update, status, and report commands across single node, multiple nodes, stdin, batch in-service datanodes, JSON output, and failure cases.

Important APIs and types: `DiskBalancerStartSubCommand`, `DiskBalancerStopSubCommand`, `DiskBalancerUpdateSubCommand`, status/report commands, `DiskBalancerSubCommandUtil`, static Mockito mocks, `ReconfigureProtocol`, `DiskBalancerConfigurationProto`, `DatanodeDiskBalancerInfoProto`, volume info protos, Picocli, and captured stdout/stderr.

Control flow: A `DiskBalancerMocks` helper mocks SCM datanode discovery, single-node reconfigure proxies, and all-operable-node lookup. Tests parse command options, execute commands, and assert result text or JSON. Start/update build configuration from threshold, bandwidth, parallelism, and disk balancing flag; stop calls the stop RPC; status/report read generated/random status protos; failures throw or print per-node errors depending on command path.

State and persistence behavior: No real datanode state. Mock protocol responses model disk balancer runtime state, volume density, ideal usage, capacities, utilization, and configuration. Static mocks are closed via AutoCloseable to avoid leakage.

Dependencies and integration points: Exercises CLI integration with datanode reconfigure protocol and SCM node discovery, including batch operations over in-service datanodes and JSON serialization of command results.

Risks: Heavy static mocking can leak if not closed. Randomized report/status protos increase coverage but can make debugging output variable. Tests assert key JSON fields rather than full schemas. Some failure paths report text rather than exception behavior.

Test signals: Start/update/stop success for batch and explicit hosts, duplicate host handling, stdin host parsing, JSON fields for action/status/configuration/report volumes, invalid container-state update error, status/report for multiple nodes, and connection/stop/update/report failure messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestDiskBalancerSubCommands.java -->
