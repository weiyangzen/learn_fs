# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeOptionParsing.java

## Purpose
Unit tests for `NameNode.parseArguments` startup option parsing, covering upgrade options, reserved path rename mappings, rolling upgrade modes, and format interactivity/force flags.

## Important APIs, Types, and Functions
- Exercises `NameNode.parseArguments`.
- Validates `HdfsServerConstants.StartupOption` values and `RollingUpgradeStartupOption`.
- Inspects `StartupOption.getClusterId`, `getRollingUpgradeStartupOption`, `getInteractiveFormat`, and `getForceFormat`.
- Checks `FSImageFormat.renameReservedMap` for `-renameReserved` behavior.

## Control Flow
- `testUpgrade` parses `-upgrade` alone, with `-clusterid`, with explicit `-renameReserved`, in alternate argument order, and with default rename values based on layout version. It then asserts error messages for unknown reserved paths and invalid rename targets, and null for `-cid`.
- `testRollingUpgrade` expects null for missing subcommand, correct options for `started` and `rollback`, and `IllegalArgumentException` for unknown subcommand.
- `testFormat` verifies default interactive format, non-interactive mode, force mode, and invalid lone `-nonInteractive`.

## State and Persistence Behavior
- Pure parser state, except static `FSImageFormat.renameReservedMap` is populated and manually cleared in part of the upgrade test.

## Dependencies and Integration Points
- Protects NameNode CLI startup option semantics used by real NameNode process startup and upgrades.

## Risks and Edge Cases
- Static `renameReservedMap` can leak entries if a failing assertion interrupts before clear points.
- Some exception branches catch expected exceptions but do not fail if no exception is thrown for two upgrade invalid cases unless later behavior exposes it.

## Test Signals
- Fast parser-level signal for upgrade, rolling upgrade, and format CLI compatibility.
