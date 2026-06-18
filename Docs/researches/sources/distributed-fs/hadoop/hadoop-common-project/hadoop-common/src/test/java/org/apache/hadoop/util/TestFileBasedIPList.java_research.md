<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestFileBasedIPList.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestFileBasedIPList.java

## Purpose

`TestFileBasedIPList.java` tests parsing and membership checks for IP and CIDR entries stored in a file.

## Important APIs, Types, and Functions

It uses `FileBasedIPList`, `IPList.isIn`, static helpers `createFileWithEntries` and `removeFile`, and Apache Commons `FileUtils.writeLines`.

## Control Flow

Tests write `ips.txt` with IPs and subnets, create a list, and assert membership/non-membership for boundary addresses. Additional tests cover null IPs, missing/null file names, empty files, malformed files, and wrong entries expected to throw.

## State and Persistence Behavior

The suite writes and deletes `ips.txt` in the process working directory. Parsed IP/subnet state is held in the `FileBasedIPList` instance.

## Dependencies and Integration Points

It integrates with Hadoop IP list parsing, subnet matching, Apache Commons IO, and JUnit 5.

## Risks and Edge Cases

Shared filename usage can conflict under parallel execution. CIDR boundary handling, null input, missing files, and malformed entries are core edge cases.

## Test Signals

Signals include positive and negative membership for exact IPs and CIDR ranges, false for null/missing/empty inputs, and expected failure for bad file contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestFileBasedIPList.java -->
