<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/tools/federation/RouterAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/tools/federation/RouterAdmin.java

## Purpose
Command-line administration tool for Router-based HDFS federation, implementing `hdfs dfsrouteradmin` operations for mount table management, quotas, safe mode, nameservice enable/disable, refreshes, and State Store dumps.

## APIs, Types, and Functions
Extends `Configured` and implements `Tool`. Main entry uses `ToolRunner`. Command dispatch in `run()` handles `-add`, `-addAll`, `-update`, `-rm`, `-ls`, `-getDestination`, quota set/clear commands, `-safemode`, `-nameservice`, `-getDisabledNameservices`, `-refresh`, `-refreshRouterArgs`, `-refreshSuperUserGroupsConfiguration`, `-refreshCallQueue`, and `-dumpState`. Helpers parse usage/min/max args, build `AddMountAttributes`, mutate `MountTable` entries, update quotas, call safe-mode/nameservice managers, invoke generic refresh RPCs, dump State Store records, and normalize paths.

## Control Flow, State, and Persistence
`run()` validates arguments, handles local `-dumpState`, creates a `RouterClient` from the configured admin address, dispatches the command, and reports exceptions with user-facing messages plus debug logging. Mount commands read existing entries, create/update/remove records through `MountTableManager`, and rely on State Store persistence behind Router admin server. Quota commands fetch the current mount entry, merge requested quota changes with existing usage/counters, and submit an update. Refresh commands update Router caches or security/call-queue state. `dumpStateStore()` starts a local `StateStoreService`, loads the driver, iterates cached record stores, and prints PB records by primary key.

## Dependencies and Integration
Integrates with `RouterClient`, `MountTableManager`, `RouterStateManager`, `NameserviceManager`, `RouterGenericManager`, State Store services, protobuf RPC engines, generic refresh protocols, and quota helpers. It uses record/protocol classes from the same state-store stack and Hadoop security/network/configuration utilities.

## Risks and Test Signals
Parsing is index-heavy and can throw when optional values are missing; some commands print and return false rather than throwing. `setQuota()` currently rejects `QUOTA_DONT_SET` because it checks `<= 0` before the "must specify" branch, so both quotas are effectively required. Storage type quota validation checks all storage types, including unset defaults, and should be tested carefully. Strong signals include Router admin command tests, mount-table cache refresh tests, quota tests, safe-mode tests, nameservice tests, generic refresh tests, and State Store dump coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/tools/federation/RouterAdmin.java -->
