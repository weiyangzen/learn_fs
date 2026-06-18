# Research: subset-b-007510

Grouped research for HDFS administrative tool sources under `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSAdmin.java -->
# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSAdmin.java`

## Purpose

`DFSAdmin` is the main implementation behind `hdfs dfsadmin`, exposing operational HDFS administration commands to report cluster health, manage safemode, snapshots, quotas, upgrades, NameNode/DataNode refreshes, dynamic reconfiguration, balancer limits, fsimage fetches, open-file inspection, and DataNode-local maintenance operations. It extends `FsShell`, so it inherits generic Hadoop shell configuration parsing and path handling, but almost every subcommand delegates to HDFS-specific RPCs through `DistributedFileSystem`, `ClientProtocol`, `ClientDatanodeProtocol`, or refresh/reconfiguration protocols.

The class is intentionally broad: it is the command-line adapter between operator syntax and HDFS admin APIs. It has no durable state of its own; it mutates or queries NameNode/DataNode state through RPCs and prints user-facing status.

## Important APIs, Types, and Functions

- Static initialization calls `HdfsConfiguration.init()` so HDFS config defaults/resources are available before command execution.
- `DFSAdminCommand` adapts `FsShell` path iteration to HDFS-only commands by converting each `PathData.fs` to `DistributedFileSystem` with `AdminHelper.checkAndGetDFS`.
- `ClearQuotaCommand`, `SetQuotaCommand`, `ClearSpaceQuotaCommand`, and `SetSpaceQuotaCommand` parse quota arguments and call `DistributedFileSystem.setQuota` or `setQuotaByStorageType`.
- `RollingUpgradeCommand` parses `RollingUpgradeAction`, invokes `DistributedFileSystem.rollingUpgrade`, checks expected state transitions, and prints `RollingUpgradeInfo`.
- `report` collects `FsStatus`, safemode/future-generation-stamp warnings, replicated block stats, erasure-coded block-group stats, and selected DataNode reports.
- `setSafeMode` maps `enter`, `leave`, `get`, `wait`, and `forceExit` into `SafeModeAction`; with a logical HA URI, it sends the action to every NameNode in the nameservice.
- `saveNamespace`, `restoreFailedStorage`, `refreshNodes`, `finalizeUpgrade`, `getUpgradeStatus`, `metaSave`, refresh ACL/mapping/call-queue operations all special-case HA logical URIs by iterating over all NameNode proxies and aggregating failures with `MultipleIOException`.
- DataNode-facing commands (`triggerBlockReport`, `getVolumeReport`, `refreshNamenodes`, `deleteBlockPool`, `shutdownDatanode`, `evictWriters`, `getDatanodeInfo`, `getBalancerBandwidth`) use `getDataNodeProxy`.
- Dynamic reconfiguration commands (`reconfig`, `startReconfiguration*`, `getReconfigurationStatus*`, `getReconfigurableProperties*`) dispatch to `ReconfigurationProtocol` for NameNodes or `ClientDatanodeProtocol` for DataNodes, with bulk modes for `livenodes` and `decomnodes`.
- `genericRefresh` constructs a protobuf RPC proxy for `GenericRefreshProtocolPB` and translates responses via `GenericRefreshProtocolClientSideTranslatorPB`.
- `run` validates arity, initializes shell state, dispatches the selected command, normalizes exceptions into exit codes, and emits detailed stack traces only at debug log level.

## Control Flow

`main` calls `ToolRunner.run(new DFSAdmin(), argv)`. `run` requires at least one command, validates command-specific argument counts, calls `init()`, and then enters a long dispatch chain. Commands that need path expansion instantiate an inner quota command and call `runAll`; most other commands call a direct method.

Read-only/reporting paths call HDFS APIs and stream formatted output. Mutating paths parse and validate flags first, then issue a single RPC or a fan-out of RPCs under HA. HA fan-out consistently follows the same pattern: detect `HAUtilClient.isLogicalUri`, obtain all proxies for the nameservice with `HAUtil.getProxiesForAllNameNodesInNameservice`, run the operation per proxy, print per-node status, collect `IOException`s, and throw `MultipleIOException` if any node failed. Some operations, such as `metaSave`, intentionally skip standby NameNodes when the remote exception unwraps to `StandbyException`.

Bulk DataNode reconfiguration uses a fixed thread pool of five workers and a `CountDownLatch`. Each worker starts or queries reconfiguration on a DataNode IPC address from the NameNode report and increments success/failure counters. The method waits for all submissions, shuts down the executor, waits up to one minute for termination, prints an aggregate summary, and returns nonzero if any node failed.

## State and Persistence Behavior

`DFSAdmin` keeps no persistent local state. It does, however, cause persistent or cluster-visible changes:

- Namespace and edit-log persistence: `saveNamespace`, `rollEdits`, `fetchImage`, `metaSave`, `finalizeUpgrade`, and `rollingUpgrade` interact with NameNode storage/checkpoint/upgrade state.
- Quotas and EC/storage quota settings persist as namespace metadata.
- Snapshot permissions and provisioned snapshot trash mutate NameNode namespace metadata.
- Refresh operations reload in-memory NameNode state from config files or service ACL files.
- Reconfiguration starts asynchronous per-daemon reconfiguration tasks; status returns `ReconfigurationTaskStatus`.
- DataNode commands can delete block pools, refresh NameNode registrations, shut down DataNodes, evict block writers, and trigger block reports.
- Balancer bandwidth changes are explicitly non-persistent on the DataNode side.

## Dependencies and Integration Points

The class integrates with `DistributedFileSystem`, HDFS admin APIs (`HdfsAdmin`), HDFS client protocols (`ClientProtocol`, `ClientDatanodeProtocol`, `ReconfigurationProtocol`), HA utilities (`HAUtil`, `HAUtilClient`), NameNode proxy construction, Hadoop IPC refresh protocols, `TransferFsImage`, security principal selection via `CommonConfigurationKeys.HADOOP_SECURITY_SERVICE_USER_NAME_KEY`, and `ToolRunner`/`FsShell`. It also prints topology information based on `DatanodeInfo` network locations and uses `DFSUtilClient` helpers to create DataNode and reconfiguration protocol proxies.

## Risks and Edge Cases

- Command validation is manual and duplicated between `run`, `printUsage`, and `printHelp`; new commands can easily drift across those tables.
- Many HA commands fan out to every NameNode. Partial success leads to cluster changes on some NameNodes before `MultipleIOException` is thrown.
- `setSafeMode wait` loops every five seconds without an external timeout and treats interruption as an `IOException`.
- Bulk reconfiguration submits one task per DataNode to a fixed five-thread pool. Large clusters can make command duration long, and output from parallel tasks shares the same `PrintStream`.
- `RollingUpgradeCommand.run` indexes `argv[1]` even though its signature accepts `idx`; with invalid/empty action usage this depends on prior dispatcher validation.
- DataNode commands accept raw host:port strings and depend on the caller using the correct IPC port.
- `genericRefresh` returns from inside a `finally` only when no response was obtained; care is needed if refactoring to avoid suppressing exceptions incorrectly.
- Some commands print success after RPC completion but do not perform independent verification of the server-side outcome.

## Test Signals

Useful tests are CLI dispatch/arity coverage for every command, HA fan-out tests with mixed active/standby/failing NameNode proxies, quota option parsing including storage type validation, safemode wait interruption behavior, bulk reconfiguration success/failure aggregation, DataNode proxy principal selection, and regression coverage that `printUsage`/`printHelp` stay aligned with `run`. Existing structure exposes several package-visible reconfiguration helpers that are testable with injected streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSHAAdmin.java -->
# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSHAAdmin.java`

## Purpose

`DFSHAAdmin` extends the generic Hadoop `HAAdmin` command set with HDFS-specific target resolution, security configuration, observer-state support, and failover behavior. It backs HDFS HA administrative commands such as `-transitionToObserver` and an HDFS-tailored `-failover`.

## Important APIs, Types, and Functions

- `addSecurityConfiguration` wraps the incoming configuration in `HdfsConfiguration`, loads HDFS resources, and sets the service principal to `dfs.namenode.kerberos.principal`.
- `resolveTarget` returns an `NNHAServiceTarget` for a NameNode ID and optional nameservice ID.
- `runCmd` parses optional `-ns <nameserviceId>`, merges generic `HAAdmin` usage with HDFS-only commands, handles `-help`, adds command-specific Apache Commons CLI options, and dispatches HDFS-only commands.
- `getTargetIds` returns NameNode IDs for the selected nameservice through `DFSUtilClient.getNameNodeIds`.
- `transitionToObserver` validates one target, verifies observer support and manual state-management safety, and calls `HAServiceProtocolHelper.transitionToObserver`.
- `failover` resolves source and destination targets, sets intended HA statuses, checks consistent auto-failover configuration, either asks ZKFCs for graceful failover or uses `FailoverController`.

## Control Flow

`main` invokes `ToolRunner.run`. `setConf` always applies HDFS security configuration before `HAAdmin` sees the config. `runCmd` consumes `-ns` if present, validates parameters against merged usage, delegates generic commands to `super.runCmd`, and handles only HDFS-specific commands locally. Mutative commands can accept `--forcemanual`, in which case the tool asks for confirmation and marks the request source as user-forced before issuing state transitions.

For `-failover`, the control path rejects malformed option/argument combinations, resolves both `NNHAServiceTarget`s, checks that both agree on auto-failover, and then chooses either ZKFC-mediated failover or manual `FailoverController.failover`.

## State and Persistence Behavior

The class stores only the optional `nameserviceId` and inherited output/request-source state. It changes cluster state through HA service RPCs: observer transition and failover alter NameNode HA state, can trigger fencing, and can involve ZKFC coordination. The local `Configuration` is copied during security setup rather than mutating the caller's original instance.

## Dependencies and Integration Points

It depends on Hadoop HA classes (`HAAdmin`, `HAServiceTarget`, `HAServiceProtocol`, `FailoverController`), Commons CLI, `NNHAServiceTarget`, `DFSUtilClient`, `DFSUtil`, and HDFS config constants. It is tightly coupled to ZKFC auto-failover semantics through `gracefulFailoverThroughZKFCs` inherited from `HAAdmin`.

## Risks and Edge Cases

- `nameserviceId` must be provided for multi-nameservice HA configs where it cannot be inferred; otherwise target resolution fails later.
- The command intentionally disallows `--forcefence` and `--forceactive` when auto-failover is enabled.
- Observer support is hard-coded through the target's `supportObserver`, currently true in `NNHAServiceTarget`; future service types would need care.
- Incorrect request-source handling could allow or block manual HA changes when auto-failover is configured.

## Test Signals

Tests should cover `-ns` parsing, merged usage validation, security principal injection without mutating the original config, manual versus auto-failover flows, rejection of unsupported auto-failover force flags, observer transition argument validation, and `getTargetIds` behavior under single and multiple nameservices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSHAAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSZKFailoverController.java -->
# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSZKFailoverController.java`

## Purpose

`DFSZKFailoverController` is the HDFS-specific `ZKFailoverController` implementation used by NameNode HA. It maps HDFS NameNode identity into ZooKeeper active-node records, binds the ZKFC RPC endpoint, logs in as the NameNode principal, enforces HDFS admin ACLs, and adds diagnostics such as local NameNode thread dumps on health failures.

## Important APIs, Types, and Functions

- `dataToTarget` parses `ActiveNodeInfo` protobuf data from ZooKeeper, reconstructs an `NNHAServiceTarget`, verifies the stored host/port matches current configuration, and restores the peer ZKFC port.
- `targetToData` serializes the active target address, ZKFC port, nameservice ID, and NameNode ID into `ActiveNodeInfo`.
- `getRpcAddressToBindTo` chooses the ZKFC bind host from service RPC bind host, NameNode RPC bind host, or the local target address, and combines it with `dfs.ha.zkfc.port`.
- `create` validates HA is enabled for the local nameservice, discovers the local NameNode ID, initializes generic NameNode keys, applies ZKFC config keys, and constructs the local target.
- `initRPC` stores the actual bound RPC port back into the local target.
- `loginAsFCUser` logs in using NameNode keytab/principal settings.
- `checkRpcAdminAccess` allows callers in `dfs.admin` or the ZKFC login user and rejects others with `AccessControlException`.
- `getLocalNNThreadDump` fetches the local NameNode `/stacks` HTTP endpoint when health changes to unhealthy/not responding.
- `getAllOtherNodes` constructs `NNHAServiceTarget`s for other NameNodes in the same nameservice.
- `isSSLEnabled` checks common and HDFS-specific ZooKeeper client SSL keys.

## Control Flow

`main` prints startup/shutdown messages, handles help, parses generic options into `HdfsConfiguration`, creates the controller, and runs inherited ZKFC logic. Controller creation is local-NameNode oriented: it must determine the nameservice and NameNode ID of the daemon host, then build an `NNHAServiceTarget` for that local NN.

The inherited ZKFC election/health loop calls `targetToData` when publishing active identity, `dataToTarget` when reading another active from ZooKeeper, `getRpcAddressToBindTo` while starting RPC, and `checkRpcAdminAccess` on incoming admin RPCs. Health state transitions route through `setLastHealthState`, which invokes thread-dump capture when the new state is unhealthy or not responding.

## State and Persistence Behavior

Local state includes `adminAcl`, `localNNTarget`, and a test-visible `isThreadDumpCaptured` flag. Cluster/persistent state lives outside the class: active-node identity is stored in ZooKeeper as `ActiveNodeInfo`, ZKFC RPC server state is in the inherited controller, and diagnostics are written to logs. The thread-dump capture is read-only against NameNode HTTP and writes only to ZKFC logs.

## Dependencies and Integration Points

The class integrates with ZooKeeper HA machinery through `ZKFailoverController`, HDFS HA target metadata via `NNHAServiceTarget`, NameNode config initialization, `HDFSPolicyProvider` for RPC service authorization, Kerberos login via `SecurityUtil`, HTTP diagnostics through `DFSUtil.getInfoServer`, and protobuf `ActiveNodeInfo`.

## Risks and Edge Cases

- `dataToTarget` deliberately fails fast if ZooKeeper active-node data conflicts with local config; this catches stale/misconfigured ZK records but can make failover unavailable until corrected.
- If `dfs.ha.zkfc.nn.http.timeout` is zero, thread-dump capture is disabled; otherwise unhealthy transitions synchronously attempt HTTP connection/read with the configured timeout.
- ACL checks rely on short username equality for the ZKFC login user and configured `dfs.admin` ACLs.
- Bind-host selection must match deployment network expectations; a wrong bind host can make graceful failover RPC unreachable.
- `setZkfcPort` in the target requires auto-failover enabled.

## Test Signals

Tests should verify protobuf round-trip, mismatch detection, bind-host fallback order, HA-disabled/local-NN-ID failure cases, admin ACL acceptance/rejection, thread-dump capture success/failure/timeouts, `getAllOtherNodes` construction, and SSL key precedence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSZKFailoverController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSck.java -->
# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSck.java`

## Purpose

`DFSck` implements the `hdfs fsck` client. It translates CLI options into NameNode HTTP `/fsck` query parameters, connects to the active NameNode info server, streams fsck output, and returns status codes based on the final NameNode fsck status line. It is a command adapter over server-side `NamenodeFsck`; it does not inspect blocks directly.

## Important APIs, Types, and Functions

- Constructors capture the current `UserGroupInformation`, output stream, timeout-configured `URLConnectionFactory`, and SPNEGO-enabled flag.
- `run` executes `doWork` as the current user.
- `listCorruptFileBlocks` repeatedly calls the `/fsck` endpoint using the `startblockafter` cookie protocol until the server indicates no more corrupt files.
- `getResolvedPath` resolves the user path with the configured filesystem.
- `getCurrentNamenodeAddress` validates the path's filesystem is `DistributedFileSystem` and finds the active NameNode info-server URI via `HAUtil.getAddressOfActive`.
- `doWork` parses fsck options, assembles the URL, opens the connection with optional SPNEGO, streams output, and maps final status text to exit codes.
- `main` handles help and the special ambiguity where `-files` is also consumed by generic option parsing.

## Control Flow

If no path is supplied, `doWork` defaults to `/`. Each recognized flag appends a corresponding query parameter. `-blockId` consumes subsequent non-option tokens into one encoded block ID value. The target path is resolved, stripped of scheme/authority, URL-encoded, and appended as `path=...`. The tool prints the full NameNode URL to stderr, then either enters the corrupt-block listing loop or streams the normal fsck response line by line.

Exit code is derived from the final line: healthy, nonexistent, excess, or bad block ID format map to success; corrupt maps to 1; decommissioned, decommissioning, in-maintenance, entering-maintenance, and stale map to distinct positive codes.

## State and Persistence Behavior

`DFSck` has no durable local state. Server-side operations may mutate HDFS only when the user passes options such as `-move`, `-delete`, or `-replicate`; those changes are performed by NameNode fsck logic. The client stores only connection settings and the authenticated user for the process lifetime.

## Dependencies and Integration Points

It depends on `NamenodeFsck` status constants, HDFS info-server discovery through `DFSUtil` and `HAUtil`, `URLConnectionFactory` for timeout/SPNEGO HTTP, `DistributedFileSystem` detection, `Path` resolution, and `ToolRunner`. Server behavior is an external contract encoded in URL parameter names and text status suffixes.

## Risks and Edge Cases

- The client infers exit status from text output suffixes; changes to server output strings can break exit-code semantics.
- `listCorruptFileBlocks` parses a tab-separated `Cookie:` line as an integer and stops on parse errors.
- If the filesystem is inaccessible or not HDFS, the command prints an error and returns `0` after "DFSck exiting.", preserving legacy behavior but surprising automation.
- `-blockId` parsing consumes multiple non-option tokens and appends spaces before URL encoding.
- The full fsck URL, including path and query flags, is printed to stderr.

## Test Signals

Tests should cover URL generation for every flag, SPNEGO connection errors, status-line-to-exit-code mapping, corrupt-block cookie iteration, access-denied output, non-HDFS filesystem behavior, default path selection, and the `-files` main-method special case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DFSck.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DebugAdmin.java -->
# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DebugAdmin.java`

## Purpose

`DebugAdmin` implements `hdfs debug`, a collection of advanced diagnostic and recovery commands: metadata checksum verification, metadata checksum generation, lease recovery, and erasure-coded block-group verification. These commands are explicitly unstable and risky; several operate directly on block metadata files or DataNode block readers.

## Important APIs, Types, and Functions

- `DebugCommand` is the small command interface with name, usage, help, and `run`.
- `VerifyMetaCommand` reads a DataNode block metadata file header, reports checksum type, and optionally verifies checksum chunks against a local block file.
- `ComputeMetaCommand` creates a metadata file for a local block file using checksum options from configuration and `FsDatasetUtil.computeChecksum`.
- `RecoverLeaseCommand` opens a filesystem for the path URI, requires `DistributedFileSystem`, and retries `recoverLease` up to `-retries`.
- `VerifyECCommand` validates a closed erasure-coded file by reading each internal block from DataNodes, recomputing parity with a raw erasure encoder, and comparing computed parity buffers to stored parity blocks.
- `popCommand`, `run`, and `printUsage` implement command dispatch and generic help.

## Control Flow

`main` runs the `DebugAdmin` tool. `run` converts argv to a mutable list, removes the first matching command, and invokes it. Unknown/no command prints usage and returns success-like `0`, while command I/O/runtime failures print stack summaries and return `1`.

`verifyMeta` reads the metadata header first. If no `-block` is supplied, it stops after printing checksum type. With a block file, it reads data chunks and matching checksum bytes in buffers, then calls `DataChecksum.verifyChunkedSums` until EOF.

`computeMeta` validates the input block exists and output metadata does not exist, writes a metadata header, closes it, then asks `FsDatasetUtil.computeChecksum` to fill checksums.

`recoverLease` loops until recovery succeeds or retries are exhausted, sleeping five seconds between attempts with `Uninterruptibles.sleepUninterruptibly`.

`verifyEC` loads file status and located blocks, rejects missing/non-file/open/non-EC files, creates a raw encoder and thread-pool-backed `CompletionService`, then for each selected block group parses internal blocks, creates block readers, reads all data/parity buffers in parallel, zero-fills short reads, encodes data into parity outputs, and compares parity buffers. Readers are closed after each group.

## State and Persistence Behavior

`VerifyMetaCommand` is read-only. `ComputeMetaCommand` creates a local metadata file and is dangerous if used to replace real DataNode metadata. `RecoverLeaseCommand` mutates NameNode lease state for the target HDFS file. `VerifyECCommand` is intended read-only against HDFS blocks but opens direct DataNode peers and consumes cluster/network resources. The `VerifyECCommand` object holds per-run DFS client, EC layout, encoder, read service, and block reader arrays.

## Dependencies and Integration Points

The file integrates with DataNode metadata classes (`BlockMetadataHeader`, `FsDatasetUtil`), HDFS client internals (`DFSClient`, `BlockReaderRemote`, `LocatedStripedBlock`, `StripedBlockUtil`), erasure coding (`CodecUtil`, `RawErasureEncoder`, `ErasureCoderOptions`), direct DataNode networking (`Peer`, block tokens), `DistributedFileSystem`, and Hadoop checksum utilities.

## Risks and Edge Cases

- `computeMeta` can make corrupt data appear valid if operators overwrite real metadata with generated checksums.
- `VerifyECCommand` assumes at least one location for each internal block and uses the first location only; unavailable first replicas can fail verification even if other replicas exist.
- The read executor created for EC verification is not explicitly shut down in this class, which can matter for repeated in-process invocations.
- Parity comparison uses `ByteBuffer.equals`, so positions/limits must remain exactly aligned.
- Assertions check checksum consistency but are disabled unless Java assertions are enabled.
- Direct block reading and one-minute future waits can hang or fail under slow DataNodes.

## Test Signals

Tests should cover metadata header parse failures, checksum mismatch offsets, output-file-exists protection, lease retry behavior and non-HDFS rejection, EC verification on healthy and corrupted stripes, missing internal block handling, first-location failure behavior, `-skipFailureBlocks`, `-blockId` filtering, and cleanup of block readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DebugAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DelegationTokenFetcher.java -->
# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DelegationTokenFetcher.java`

## Purpose

`DelegationTokenFetcher` implements the legacy `fetchdt` utility for fetching, printing, renewing, or canceling HDFS delegation tokens stored in a local token file. It works with the default filesystem or an explicitly supplied WebHDFS/SWebHDFS URL.

## Important APIs, Types, and Functions

- `main(Configuration, String[])` builds Commons CLI options, parses generic Hadoop options, validates mode selection, resolves the local output token path, and runs the requested action as the current user.
- `getFileSystem` maps `http://` and `https://` webservice URLs to `webhdfs://` and `swebhdfs://` schemes for backward compatibility.
- `saveDelegationToken` calls `FileSystem.getDelegationToken`, writes a `Credentials` file in writable token-storage format, and logs debug details.
- `cancelTokens` and `renewTokens` iterate token storage and call `cancel` or `renew` only for managed tokens.
- `printTokensToString` decodes identifiers and prints a stable or verbose delegation-token identifier string.
- `printUsage` emits help and calls `ExitUtil.terminate(1)`.

## Control Flow

The CLI accepts at most one of `--cancel`, `--renew`, and `--print`; with none of those, it fetches a new token. It requires exactly one non-option token file name and resolves it against the local filesystem working directory. All actions run in a `UserGroupInformation.doAs` block. Fetch mode obtains the target filesystem from config or `--webservice`; other modes read the token file.

## State and Persistence Behavior

The durable artifact is the token storage file. Fetch mode writes or overwrites that file with a single fetched token. Renew and cancel mutate server-side token state for managed tokens. Print mode is read-only. No long-lived process state is kept.

## Dependencies and Integration Points

The class integrates with Hadoop `FileSystem` delegation-token APIs, `Credentials` token storage, HDFS delegation token identifiers for stable printing, WebHDFS constants, `GenericOptionsParser`, `UserGroupInformation`, and `ExitUtil`.

## Risks and Edge Cases

- Invalid usage often returns from `main(Configuration, ...)` after printing rather than terminating, except `printUsage` itself calls `ExitUtil.terminate(1)`.
- Fetch mode silently does not write a file if `getDelegationToken` returns null and only prints an error.
- `remaining[0].charAt(0)` assumes the remaining token filename is non-empty.
- `printTokensToString` calls `decodeIdentifier`; unknown token formats can throw.
- Renew/cancel only act on managed tokens, so a mixed token file may leave some tokens untouched without explicit user output.

## Test Signals

Tests should cover mutually exclusive mode validation, webservice URL scheme conversion, local token path resolution, token file serialization format, stable versus verbose token printing, managed/unmanaged renew/cancel behavior, and `ExitUtil` behavior under disabled system exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DelegationTokenFetcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DiskBalancerCLI.java -->
# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DiskBalancerCLI.java`

## Purpose

`DiskBalancerCLI` is the top-level command dispatcher for HDFS disk balancer operations. It defines CLI options for planning, executing, querying, canceling, reporting, and help, then delegates implementation to command classes under `org.apache.hadoop.hdfs.server.diskbalancer.command`.

## Important APIs, Types, and Functions

- Public constants define command and option names, output filename templates, default report count, and plan version.
- Static `Options` instances expose per-command option sets for tests and help generation.
- `run` composes all options, parses args with Commons CLI `BasicParser`, rejects extra positional arguments beyond two, and dispatches.
- `addPlanCommands`, `addExecuteCommands`, `addQueryCommands`, `addCancelCommands`, `addReportCommands`, and `addHelpCommands` populate both global and per-command option collections.
- `dispatch` selects `PlanCommand`, `ExecuteCommand`, `QueryCommand`, `CancelCommand`, `ReportCommand`, or `HelpCommand`, executes it, and always closes it.

## Control Flow

`main` runs the tool with `HdfsConfiguration` and converts thrown exceptions into process exit code `1`. `run` parses all recognized command options at once rather than subcommand-first parsing. `dispatch` checks options in fixed order and assigns `dbCmd` when an option is present; if multiple command options are present, the later matching checks can override earlier ones. If no command option exists, it executes main help and returns `1`.

## State and Persistence Behavior

`DiskBalancerCLI` stores `printStream` and a `currentCommand` field, though the field is not assigned in the shown dispatch path. Persistent/cluster state is handled by delegated command classes: plan/report may write files, execute/cancel/query talk to DataNodes and HDFS. This class itself only parses and dispatches.

## Dependencies and Integration Points

It depends on Apache Commons CLI, Hadoop `Configured`/`Tool`, `HdfsConfiguration`, and disk balancer command implementations. Constants here form part of the contract consumed by those commands and tests.

## Risks and Edge Cases

- Static `Options` instances are mutated every time `add*Commands` is called, so repeated `run` calls in the same JVM can accumulate duplicate options depending on Commons CLI behavior.
- Multiple top-level command options are not rejected directly; last matching command in dispatch order wins.
- `currentCommand` is exposed but not set, which limits observability or may break expectations in tests.
- `BasicParser` is legacy Commons CLI API.
- Extra positional argument validation allows up to two args regardless of which command is selected; deeper validation is delegated.

## Test Signals

Tests should cover each command option selecting the right command, help fallback, multi-command-option behavior, duplicate static option registration across repeated instances, parse errors, command close in failure paths, and positional argument rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DiskBalancerCLI.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/ECAdmin.java -->
# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/ECAdmin.java`

## Purpose

`ECAdmin` implements the `hdfs ec` command set for erasure coding administration: listing, adding, removing, enabling, disabling, setting, unsetting, querying policies, listing codecs, and verifying cluster topology support for EC policies.

## Important APIs, Types, and Functions

- `run` resolves an `AdminHelper.Command` from the first dash-prefixed argument, strips the command name, and invokes the command with the current configuration.
- `ListECPoliciesCommand` calls `DistributedFileSystem.getAllErasureCodingPolicies`.
- `AddECPoliciesCommand` loads policy XML through `ECPolicyLoader` and calls `addErasureCodingPolicies`.
- `GetECPolicyCommand`, `SetECPolicyCommand`, and `UnsetECPolicyCommand` resolve path-specific `DistributedFileSystem` instances and call path EC APIs.
- `RemoveECPolicyCommand`, `EnableECPolicyCommand`, and `DisableECPolicyCommand` mutate named cluster EC policies.
- `ListECCodecsCommand` calls `getAllErasureCodingCodecs`.
- `VerifyClusterSetupCommand` calls `getECTopologyResultForPolicies`, optionally with policy names after `-policy`.
- `COMMANDS` registers all subcommands for usage and dispatch.

## Control Flow

Every subcommand owns its option parsing using `StringUtils.popOptionWithArgument`, `StringUtils.popOption`, or `CommandFormat`. Most commands reject leftover args as "Too many arguments". Path commands choose DFS based on the path URI. Mutating commands catch `IOException`, prettify the exception, print to stderr, and return command-specific nonzero status.

`-setPolicy` permits either `-policy <policy>`, `-replicate`, or neither. `-replicate` maps to the replication pseudo-policy name. After setting or unsetting, it lists directory status to warn that existing files in non-empty directories are not converted automatically. `-enablePolicy` also asks the NameNode for topology support and prints a warning if the cluster cannot support the enabled policy.

## State and Persistence Behavior

All persistent state is in HDFS: EC policy definitions and enablement are cluster metadata, and path EC policy settings are namespace metadata. `-addPolicies` reads local XML policy definitions. `-verifyClusterSetup` and listing commands are read-only.

## Dependencies and Integration Points

The class integrates with `DistributedFileSystem` EC APIs, `ECPolicyLoader`, `ErasureCodingPolicy*` protocol types, `ECTopologyVerifierResult`, `NoECPolicySetException`, `ErasureCodeConstants.REPLICATION_POLICY_NAME`, `AdminHelper`, Hadoop `TableListing`, and `ToolRunner`.

## Risks and Edge Cases

- `-removePolicy` prints `"policy Xis removed"` without a space, a user-facing formatting defect.
- Directory non-empty warnings call `listStatusIterator`; permission or listing errors make the whole command fail after the policy mutation may already have succeeded.
- `-setPolicy` with neither `-policy` nor `-replicate` sets the default EC policy; callers must understand inherited/default behavior.
- `VerifyClusterSetupCommand` maps remote `HadoopIllegalArgumentException` by substring matching class name.
- Command-specific return codes are not uniform across subcommands.

## Test Signals

Tests should cover dispatch and dash-prefix validation, XML policy loading success/failure, path URI filesystem selection, `-setPolicy` option conflicts/default/replicate modes, non-empty directory warnings, `NoECPolicySetException` hint text, topology verifier supported/unsupported returns, and user-facing output regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/ECAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/GetConf.java -->
# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/GetConf.java`

## Purpose

`GetConf` implements `hdfs getconf`, a read-only utility for printing selected HDFS configuration-derived values such as NameNode, SecondaryNameNode, BackupNode, JournalNode, include/exclude file paths, NameNode RPC addresses, and arbitrary config keys.

## Important APIs, Types, and Functions

- `Command` enum defines supported user options and a static map from lower-case command name to `CommandHandler`.
- `CommandHandler` provides default no-extra-argument validation and config-key lookup behavior.
- `NameNodesCommandHandler`, `SecondaryNameNodesCommandHandler`, `BackupNodesCommandHandler`, and `JournalNodeCommandHandler` call `DFSUtil` address discovery helpers.
- `NNRpcAddressesCommandHandler` flattens configured NameNode service RPC addresses and prints `host:port`.
- `PrintConfKeyCommandHandler` requires exactly one key and delegates to default config lookup.
- `printMap` and `printSet` format address collections as space-separated output.
- `run` executes `doWork` as current user.

## Control Flow

Static initialization loads HDFS configuration and builds the usage string from enum values. `main` handles help through `DFSUtil.parseHelpArgument`, then runs the tool. `doWork` looks up a command handler by first argument; if found it passes the remaining args to the handler, otherwise it prints usage and returns `-1`.

## State and Persistence Behavior

The tool is read-only. It stores output and error streams for testability. It reads the effective Hadoop/HDFS configuration and derived address maps but writes no local or cluster state.

## Dependencies and Integration Points

It depends on `DFSUtil` config/address helpers, `DFSConfigKeys`, `HdfsConfiguration`, `UserGroupInformation`, and `ToolRunner`. It is often used by scripts, so exact stdout formatting is an integration contract.

## Risks and Edge Cases

- `printMap` emits only hostnames for many commands, while `-nnRpcAddresses` emits host:port; scripts need command-specific parsing.
- Missing config keys return `-1` and print to stderr.
- Address ordering depends on `DFSUtil.flattenAddressMap` and set iteration for journal nodes.
- Usage string says `hadoop getconf` while the modern command path is usually `hdfs getconf`.

## Test Signals

Tests should cover every enum command, case-insensitive command lookup, missing keys, extra argument rejection, multi-nameservice flattening, journal node URI parsing, stdout/stderr separation, and doAs interruption wrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/GetConf.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/GetGroups.java -->
# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/GetGroups.java`

## Purpose

`GetGroups` is the HDFS-specific implementation of the generic `GetGroupsBase` tool. It prints group memberships for one or more users by contacting the NameNode's `GetUserMappingsProtocol`.

## Important APIs, Types, and Functions

- Static initialization loads `HdfsConfiguration`.
- `getProtocolAddress` returns the NameNode address from `DFSUtilClient.getNNAddress`.
- `setConf` wraps config in `HdfsConfiguration`, sets the service principal to the NameNode Kerberos principal, and delegates to the base class.
- `getUgmProtocol` creates a NameNode proxy for `GetUserMappingsProtocol`.
- `main` handles help and uses `ToolRunner`.

## Control Flow

The inherited `GetGroupsBase` handles argument iteration and printing. This subclass supplies HDFS address/proxy construction and security configuration. The tool starts in `main`, exits early for help, then runs against a new `HdfsConfiguration`.

## State and Persistence Behavior

The tool is read-only. It mutates only its local configuration copy to set the server principal key, then performs NameNode RPCs.

## Dependencies and Integration Points

It integrates with `GetGroupsBase`, `GetUserMappingsProtocol`, `NameNodeProxies`, `DFSUtilClient`, `FileSystem.getDefaultUri`, HDFS Kerberos config keys, and `ToolRunner`.

## Risks and Edge Cases

- It depends on default filesystem/NameNode resolution; incorrect `fs.defaultFS` or HA config causes proxy failures.
- Security principal configuration must match the NameNode service or Kerberos RPC authentication fails.
- Behavior for no usernames is inherited and should be checked at base-class level.

## Test Signals

Tests should verify principal injection, correct protocol address, proxy creation configuration, help handling, output stream injection, and behavior against mocked user mapping protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/GetGroups.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/HDFSConcat.java -->
# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/HDFSConcat.java`

## Purpose

`HDFSConcat` is a small standalone utility that invokes `DistributedFileSystem.concat` for a target path and one or more source paths. It appears to be a simple manual/test helper rather than a full `ToolRunner` command.

## Important APIs, Types, and Functions

- `def_uri` defaults to `hdfs://localhost:9000`.
- `main` validates at least two args, reads `fs.default.name` with fallback to `def_uri`, obtains a `DistributedFileSystem`, converts all remaining args to `Path[]`, and calls `dfs.concat(target, srcs)`.

## Control Flow

The utility exits with status `0` after printing usage if fewer than two args are supplied. Otherwise it constructs a plain `Configuration`, resolves the filesystem from a path built from the default URI, casts it to `DistributedFileSystem`, builds source paths, and performs the concat.

## State and Persistence Behavior

The utility mutates HDFS namespace/block metadata by concatenating source files into the target according to HDFS concat semantics. It keeps no local state.

## Dependencies and Integration Points

It depends on the older `fs.default.name` configuration key, `FileSystem.get`, `DistributedFileSystem.concat`, and `Path`.

## Risks and Edge Cases

- The cast to `DistributedFileSystem` fails for non-HDFS default filesystems.
- It uses the legacy `fs.default.name` key rather than newer `fs.defaultFS`.
- Usage errors exit `0`, which can confuse scripts.
- No generic options, Kerberos setup, detailed validation, or user-friendly error handling are provided.

## Test Signals

Tests should cover argument validation exit behavior, default URI resolution, non-HDFS cast failure, target/source path construction, and concat invocation against a mini HDFS cluster.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/HDFSConcat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/JMXGet.java -->
# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/JMXGet.java`

## Purpose

`JMXGet` is a command-line utility for querying Hadoop MBeans, typically NameNode or DataNode metrics, either from the local platform MBean server, an RMI JMX server, or an explicit local VM connector URL.

## Important APIs, Types, and Functions

- Setters configure service, port, server, and local VM connector URL.
- `init` builds a JMX service URL or uses the platform MBean server, connects, logs domains/counts to stderr, and queries `Hadoop:service=<service>,*` object names.
- `printAllValues` prints every attribute from all matched object names.
- `printAllMatchedAttributes` prints attributes whose names match a regular expression prefix via `lookingAt`.
- `getValue` returns the first matching attribute value across queried object names, ignoring missing attributes and missing getter reflections.
- `parseArgs` defines Commons CLI options and parses remaining metric keys.
- `main` configures the instance, handles help, initializes, and prints either all values or requested keys.

## Control Flow

CLI parsing accepts `-service`, `-server`, `-port`, `-localVM`, and `-help`. If no port/local VM is supplied, `init` uses the same JVM's platform MBean server, which is useful for tests. Otherwise it constructs an RMI URL or uses the supplied connector URL. After querying object names, `main` prints all attributes when no keys are supplied; otherwise it prints `key=value` for each requested key.

## State and Persistence Behavior

The utility is read-only. It stores the JMX connection and matched object names for one run. It does not close the `JMXConnector` explicitly after connecting, because the connector object is local to `init`.

## Dependencies and Integration Points

It integrates with Java Management Extensions (`MBeanServerConnection`, `ObjectName`, `JMXConnectorFactory`), Commons CLI, Hadoop `ExitUtil`, and the Hadoop MBean naming convention under the `Hadoop` domain.

## Risks and Edge Cases

- The JMX connector is not retained/closed, which can leak resources during repeated in-process use.
- `printAllValues` does not catch per-attribute read failures; one bad attribute can abort the run.
- Query domain is capitalized `Hadoop`, matching Hadoop metrics but not arbitrary MBeans.
- Logging and diagnostics go to stderr, while values go to stdout; scripts should separate streams.
- `getValue` suppresses missing-attribute cases across beans and returns an empty string when none match.

## Test Signals

Tests should cover local platform MBean queries, RMI URL construction, localVM URL use, command parsing errors/help, missing attribute behavior, regex filtering, stdout formatting, and connector lifecycle expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/JMXGet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/NNHAServiceTarget.java -->
# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/NNHAServiceTarget.java`

## Purpose

`NNHAServiceTarget` adapts an HDFS NameNode to the generic HA framework's `HAServiceTarget`. It resolves the NameNode service address, optional lifeline address, ZKFC address, fencing configuration, nameservice ID, and NameNode ID from configuration for use by `DFSHAAdmin`, `DFSZKFailoverController`, and HA fencing/failover logic.

## Important APIs, Types, and Functions

- Constructors initialize target NameNode config either from configured addresses or provided address strings.
- `initializeNnConfig` resolves or validates nameservice ID, copies the configuration into `HdfsConfiguration`, and calls `NameNode.initializeGenericKeys` for the target NN.
- `initializeFailoverConfig` reads auto-failover enablement, sets the ZKFC port when configured, and creates a `NodeFencer`, storing any fencing configuration error.
- `getAddress`, `getHealthMonitorAddress`, and `getZKFCAddress` expose service, lifeline, and ZKFC RPC addresses to the HA framework.
- `setZkfcPort` stores the ZKFC address using the NameNode address's IP and supplied port.
- `checkFencingConfigured` throws any stored fencing config error or a missing-fencer error.
- `addFencingParameters` adds `nameserviceid` and `namenodeid` to the inherited fencing environment map.
- `isAutoFailoverEnabled` and `supportObserver` report target capabilities.

## Control Flow

Construction first binds the target configuration to a specific nameservice/NameNode pair. If no nameservice ID is provided, the class accepts a single inferable nameservice but rejects ambiguous multi-nameservice configs with guidance to use `-ns`. It resolves the service RPC address and optional lifeline address, then initializes failover/fencing state.

The HA framework later calls getters for RPC and health-monitor endpoints, checks fencing configuration before failover, asks for the fencer, and obtains fencing parameters when executing fencing methods.

## State and Persistence Behavior

The class stores resolved target metadata and a copied configuration. It performs no persistent changes itself. Its `NodeFencer` may execute configured external fencing actions when used by HA failover code outside this class.

## Dependencies and Integration Points

It depends on `HAServiceTarget`, `NodeFencer`, HDFS config resolution in `DFSUtil`, `NameNode.initializeGenericKeys`, `DFSZKFailoverController.getZkfcPort`, `NetUtils`, and HDFS client config defaults. It is the central shared target representation for HA admin and ZKFC code in this package.

## Risks and Edge Cases

- If `dfs.nameservices` contains multiple values and no nameservice is provided, construction fails intentionally.
- Missing service address causes immediate `IllegalArgumentException`.
- `getZKFCAddress` asserts and checks auto-failover; callers must not request it for manual failover targets.
- The alternate constructor calls `NetUtils.createSocketAddr(lifelineAddr)` unconditionally, so null lifeline strings may not be safe.
- Fencing config errors are deferred until `checkFencingConfigured`, allowing target construction but later failover failure.

## Test Signals

Tests should cover nameservice inference and ambiguity errors, generic-key initialization, service/lifeline/ZKFC address resolution, auto-failover on/off behavior, fencing config success/failure deferral, fencing parameter injection, and observer capability reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/NNHAServiceTarget.java -->
