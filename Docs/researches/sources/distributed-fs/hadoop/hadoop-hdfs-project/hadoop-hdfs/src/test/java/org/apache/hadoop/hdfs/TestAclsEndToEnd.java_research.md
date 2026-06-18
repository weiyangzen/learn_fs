# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAclsEndToEnd.java

## Purpose
`TestAclsEndToEnd` validates KMS and key ACL enforcement through the full HDFS encryption-zone path. It starts real MiniKMS and MiniDFSCluster instances, switches proxy users, creates keys/zones/files, reads encrypted files, and deletes keys under allowed and denied ACL configurations.

## Important APIs, Types, and Functions
- Static setup `captureUser()` records the real UGI and user name for proxy-user configuration.
- `getKeyProviderURI()` converts the MiniKMS URL into a KMS provider URI.
- `writeConf(File, Configuration)` writes `kms-site.xml`, `kms-acls.xml`, and an empty `core-site.xml` because MiniKMS consumes config from files.
- `setup(Configuration, boolean resetKms, boolean resetDfs)` optionally creates/reuses a KMS dir, writes KMS config, starts MiniKMS, configures HDFS key-provider path and proxy users, then starts MiniDFSCluster.
- `teardown()` restores the login user, shuts down DFS, and stops MiniKMS.
- `getBaseConf`, `setBlacklistAcls`, and `setKeyAcls` build common KMS ACL matrices.
- Full-flow tests `testGoodWithWhitelist`, `testGoodWithKeyAcls`, and variants without blacklists call `doFullAclTest`.
- Focused matrix tests cover `testCreateKey`, `testCreateEncryptionZone`, `testCreateFileInEncryptionZone`, `testReadFileInEncryptionZone`, and `testDeleteKey`.
- Operation wrappers `createKey`, `createEncryptionZone`, `createFile`, `compareFile`, and `deleteKey` run actions as a target `UserGroupInformation`.
- `doUserOp` sets the login user, runs a privileged action, logs `IOException`, and returns success/failure as a boolean.

## Control Flow
The full ACL test creates proxy users for HDFS, key admin, and a normal user. It starts MiniKMS/MiniDFS with a provided ACL config, verifies key creation is limited to the key admin, creates an HDFS directory owned by the normal user, verifies only HDFS can create an encryption zone using the key, verifies only the normal user can create/read files in the zone, deletes the zone, and verifies only the key admin can delete the key.

Focused tests often use a two-phase pattern: first start with permissive setup ACLs to create a key, zone, or file; then tear down and restart with the same KMS/DFS data but a new ACL configuration to test one operation in isolation. The matrices compare whitelist ACLs, default key ACLs, key-specific ACLs overriding defaults, blacklists, missing KMS ACLs represented by a single space, missing key ACLs, and permissive default KMS ACL behavior.

## State and Persistence Behavior
The test persists KMS keystore data under `kmsDir` and HDFS namespace/data under the MiniDFSCluster base dir. Many scenarios intentionally reuse KMS data (`resetKms=false`) and sometimes DFS data (`resetDfs=false`) across service restarts to isolate ACL behavior from object creation. It also mutates global login user state through `UserGroupInformation.setLoginUser`, restoring it in teardown.

The file comments call out a persistence nuance: blank ACL values written through XML are treated as unset, so tests use `" "` to preserve a value that KMS later trims to blank. File contents are a fixed text string written into encryption zones.

## Dependencies and Integration Points
The test integrates HDFS encryption zones, MiniKMS, KMS ACL config, `KeyAuthorizationKeyProvider`, KMS client provider URIs, Java key stores, MiniDFSCluster, proxy-user settings, DFS delegation-token key behavior, UGI proxy users, DFS key creation helpers, and direct NameNode key-provider deletion. It is an end-to-end bridge between KMS authorization and HDFS encrypted file operations.

## Risks and Edge Cases
- There is no JUnit `@AfterEach`; cleanup is manual in each test/finally block. A setup failure before `miniKMS` exists or before `fs` exists could make teardown paths fragile.
- Global login-user mutation can leak across tests if teardown is skipped.
- Tests rely on KMS/DFS data reuse across restarts; accidental reset flags can invalidate scenarios.
- Assertions such as `new File(kmsDir, "kms.keystore").length() == 0` appear before `setup(conf)` in some tests, so they rely on prior static/instance state and may be brittle under unusual test-instance lifecycles.
- Boolean wrappers collapse all `IOException`s into denied/failed outcomes; they prove authorization at a high level but may hide a non-ACL I/O problem unless logs are inspected.
- Direct key deletion through `cluster.getNameNode().getNamesystem().getProvider().deleteKey` bypasses higher-level filesystem APIs by design.

## Test Signals
Passing tests confirm KMS ACLs, key ACLs, default ACLs, blacklists, and key-specific override semantics across key creation, encryption-zone creation, encrypted file creation, encrypted file read, and key deletion. Failure messages identify the ACL dimension being tested; logs from `doUserOp` provide the concrete `IOException`.
