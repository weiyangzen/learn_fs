# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testErasureCodingConf.xml

## Purpose

`testErasureCodingConf.xml` is the HDFS erasure-coding CLI test definition. The complete 1086-line file was read. It defines 58 tests for `hdfs ec` usage/help, policy set/unset/get/list/add/enable/disable/remove command behavior, invalid parameter handling, codec listing, and `count -e`/`ls -e` display of erasure-coding policy.

## Important APIs, Types, and Functions

The fixture uses `<ec-admin-command>` and DFS shell commands. EC commands include usage/help for subcommands, `-setPolicy`, `-unsetPolicy`, `-getPolicy`, `-listPolicies`, `-addPolicies`, `-removePolicy`, `-enablePolicy`, `-disablePolicy`, and `-listCodecs`. DFS shell commands include `-mkdir`, `-touchz`, `-rm`, `-rmdir`, `-count -e -v`, and `-ls -e`. It references built-in policies such as `RS-6-3-1024k`, `RS-3-2-1024k`, `REPLICATION`, and user-added policies from a policy file including `XOR-2-1-128k`, `RS-12-4-128k`, and `RS-LEGACY-12-4-128k`.

## Control Flow

The first ten tests validate usage and help text for the top-level command and subcommands. Policy behavior tests set policies on directories, repeat setting, set replication policy, unset and get policy, change policy, warn on non-empty directories, handle inherited policies, reject unsetting where no explicit policy exists, and query files/directories with and without EC policy. Policy management tests list built-ins, add user policies, list disabled user policies, enable/disable policies idempotently, and validate illegal/missing/extra parameters for set/get/list/add/enable/disable/listCodecs. Final tests verify codec listing and show EC policy in `count -e -v` and `ls -e`, including directories, files, disabled policy display, and replication policy display.

## State and Persistence Behavior

The fixture mutates NameNode EC policy xattrs on directories, creates files inheriting EC policy, adds user-defined policies to the EC policy manager, toggles policy enabled/disabled state, and relies on cleanup of `/ecdir`, `/dir1`, and `/file1`. Some operations intentionally leave global EC policy manager state changed for later list/enable/disable assertions within the same CLI suite.

## Dependencies and Integration Points

It integrates with `ECAdmin`, NameNode erasure-coding policy manager, filesystem xattr storage for policy assignments, DFS shell `count` and `ls` formatting, policy-file parsing, codec registry, and CLI comparator framework.

## Risks and Edge Cases

Risks include policy-name matching drift, warning text changes for non-empty directories, inherited versus explicit policy confusion, allowing `-replicate` with `-policy`, disabled policy display regressions, global policy state leaking across tests, codec registry differences by runtime, and exact regex assumptions for formatted `ls -e`/`count -e` columns.

## Test Signals

Signals include expected help text, policy set/unset/get messages, non-empty directory warnings, `NoECPolicySetException`, policy-list entries and `State=DISABLED`, add-policy success/failure messages, idempotent enable/disable strings, invalid-argument diagnostics, codec listing header, and regex matches showing EC policy columns in `count` and `ls`.
