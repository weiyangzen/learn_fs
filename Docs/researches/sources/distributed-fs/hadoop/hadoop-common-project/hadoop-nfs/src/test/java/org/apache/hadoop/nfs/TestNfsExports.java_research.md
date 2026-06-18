<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/TestNfsExports.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/TestNfsExports.java

## Purpose

JUnit 5 tests for `NfsExports` host/address matcher parsing, privilege selection, and cache expiry. The source was read as a complete 222-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class TestNfsExports`, `public void testWildcardRW()`, `public void testWildcardRO()`, `public void testExactAddressRW()`, `public void testExactAddressRO()`, `public void testExactHostRW()`, `public void testExactHostRO()`, `public void testCidrShortRW()`, `public void testCidrShortRO()`, `public void testCidrLongRW()`.

## Control Flow

Each test constructs `NfsExports` with wildcard, exact address/host, CIDR, regex, grouped regex, or multiple matcher strings and asserts `AccessPrivilege`; invalid syntax tests assert IllegalArgumentException.

## State and Persistence Behavior

Test-only state is local to each test method. No persistent files are created.

## Dependencies and Integration Points

Direct dependencies include `Nfs3Constant`, `Assertions`, `Test`. Integration points are JUnit 5, AssertJ where used, and the Hadoop NFS classes under test.

## Risks and Edge Cases

`testMultiMatchers` sleeps and polls around cache expiration, so it can be timing-sensitive on slow CI; hostname regex cache behavior is intentionally asserted.

## Test Signals

This file itself is a test signal; additional coverage should include negative/malformed XDR and more edge cases around cache expiry or file handle contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/test/java/org/apache/hadoop/nfs/TestNfsExports.java -->
