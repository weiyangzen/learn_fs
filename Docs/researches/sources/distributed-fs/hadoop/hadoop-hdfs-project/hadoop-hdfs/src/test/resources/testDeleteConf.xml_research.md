# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testDeleteConf.xml

## Purpose

`testDeleteConf.xml` is an HDFS CLI test definition for recursive delete behavior with and without `-safely`. The complete 83-line file was read. It defines two tests that build small directory trees and verify expected delete output.

## Important APIs, Types, and Functions

The fixture uses DFS shell commands `-mkdir`, `-copyFromLocal`, `-ls`, and `-rm -r` with and without `-safely`. It depends on `CLITEST_DATA/data15bytes`, `data30bytes`, `data60bytes`, and `data120bytes`. It uses `RegexpComparator` to match `Deleted /dir0`.

## Control Flow

The first test creates `/dir0` with four files and two child directories, lists it, then deletes recursively without `-safely`; even though the tree meets warning criteria, the expected output is deletion. The second test creates a slightly smaller tree that does not meet warning criteria and deletes with `-safely`; it also expects deletion. Cleanup tries to remove `/dir0` in both cases in case the main delete fails.

## State and Persistence Behavior

The tests create transient HDFS files and directories under `/dir0`. They exercise namespace deletion and Trash/safe-delete prompting behavior through the CLI, then remove all state during cleanup.

## Dependencies and Integration Points

It integrates with `FsShell` delete command parsing, HDFS namespace mutation, CLI safe-delete threshold configuration, local CLI test data resources, and regex output comparison.

## Risks and Edge Cases

Risks include safe-delete warning thresholds changing, interactive prompt behavior entering automated tests, cleanup hiding partial delete failures, and output wording drift from `Deleted /dir0`.

## Test Signals

Signals are command completion and output matching `Deleted /dir0` in both safe and non-safe recursive delete scenarios, with no leftover `/dir0` for later CLI tests.
