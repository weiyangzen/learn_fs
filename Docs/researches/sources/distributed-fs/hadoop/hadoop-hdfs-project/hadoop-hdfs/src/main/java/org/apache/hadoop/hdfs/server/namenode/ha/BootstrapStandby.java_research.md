# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/BootstrapStandby.java

## Purpose

`BootstrapStandby.java` implements the `hdfs namenode -bootstrapStandby` style tool that initializes a standby NameNode's local storage from another NameNode in an HA nameservice. The source was read as a complete 597-line file.

## Important APIs, Types, and Functions

The class implements `Tool` and `Configurable`. Key methods are `run`, `parseArgs`, `doRun`, `parseConfAndFindOtherNN`, `format`, `doPreUpgrade`, `doUpgrade`, `downloadImage`, `checkLogsAvailableForRead`, `checkLayoutVersion`, `parseProvidedConfigurations`, `formatAndDownloadAliasMap`, and static `run`. It defines error codes for connection, layout mismatch, already formatted storage, and unavailable logs. The nested `AliasMapStorageDirectory` supports formatting checks for alias map directories.

## Control Flow

`run` parses `-force`, `-nonInteractive`, and `-skipSharedEditsCheck`, disables in-progress tailing for bootstrap efficiency, validates HA/shared-edits configuration, logs in as the NameNode principal, and executes as the login user. `doRun` tries configured remote NameNodes until it obtains namespace information, upgrade state, and rolling-upgrade state. It validates layout compatibility, prints the bootstrap summary, creates `NNStorage`, formats or prepares upgrade directories, downloads fsimage and optional rollback image, writes `seen_txid`, finishes upgrade directory renames if needed, and optionally bootstraps an in-memory alias map.

## State and Persistence Behavior

The tool formats local name and edits directories, writes VERSION files, downloads fsimage files and md5 digests, writes `seen_txid`, may create `previous.tmp` and `previous` during upgrade bootstrap, and may delete/recreate the alias map directory. It checks shared edits readability from the downloaded checkpoint transaction through the active's current transaction unless skipped.

## Dependencies and Integration Points

It integrates with `HAUtil`, `DFSUtil`, `NameNodeProxies`, `NamenodeProtocol`, `NamespaceInfo`, `NNStorage`, `FSImage`, `TransferFsImage`, `NNUpgradeUtil`, `Storage.confirmFormat`, `RemoteNameNodeInfo`, `DFSHAAdmin` security configuration, and provided-storage alias map support.

## Risks and Edge Cases

Formatting is destructive and governed by `force`/`interactive`. Bootstrapping from a remote with incompatible layout must stop. Shared edits gaps can produce a standby that cannot catch up, so `checkLogsAvailableForRead` is important unless explicitly skipped. Rolling upgrade needs rollback image handling. Alias map deletion/creation must not erase data unexpectedly without confirmation.

## Test Signals

Tests should cover argument parsing, HA/shared-edits validation, active discovery with failed remotes, layout compatibility in normal and rolling upgrade modes, format confirmation combinations, already formatted storage, upgrade directory transitions, shared edits availability and skip behavior, fsimage and rollback downloads, `seen_txid`, alias map bootstrap, and secure login.
