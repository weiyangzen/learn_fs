# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestNetgroupCache.java

Purpose: Unit tests for static `NetgroupCache` membership tracking.

Important APIs/types/functions: `NetgroupCache.add`, `getNetgroups`, `clear`, `@AfterEach teardown`, and helper `verifyGroupMembership`.

Control flow: membership test adds two groups with overlapping users and verifies users map to expected group counts. User-removal test clears and re-adds a group without one user, checking removal. Group-removal test clears two groups and re-adds one, checking removed group/user no longer appears.

State and persistence: global static netgroup cache cleared after each test.

Dependencies/integration points: netgroup-aware group mapping implementations.

Risks: static cache must be cleared to avoid cross-test contamination; tests assert membership presence but not exact group ordering.

Test signals: validates user-to-netgroup reverse mapping updates correctly when cache content changes.
