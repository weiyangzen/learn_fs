# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/resources/TestParam.java

## Purpose
`TestParam` validates parsing, defaulting, validation bounds, string encoding, and configurable regex behavior for WebHDFS REST parameter classes.

## Important APIs, types, and functions
The test covers scalar params such as `AccessTimeParam`, `ModificationTimeParam`, `BlockSizeParam`, `BufferSizeParam`, `ReplicationParam`, `OverwriteParam`, `RecursiveParam`, quota params, storage policy/type, and EC policy. It covers security and metadata params such as `UserParam`, `AclPermissionParam`, `FsActionParam`, XAttr name/value/encoding/set-flag params, snapshot names, rename options, concatenation source paths, and HTTP op params. `Param.toSortedString` is checked for URI escaping and stable sorted output.

## Control flow
Each JUnit test instantiates one or more parameter objects with default, valid, and invalid values. Invalid values are expected to throw `IllegalArgumentException` or to be caught through explicit `fail()` blocks. Regex override tests save the current domain object, install a new pattern, validate previously invalid users/ACLs, and restore the original domain in a `finally` block for ACLs.

## State and persistence behavior
Most tests are pure object parsing. `UserParam.setUserPattern` and `AclPermissionParam.setAclPermissionPattern` mutate static validation domains; the ACL test restores in `finally`, while the user-pattern test explicitly resets after assertions. No file-system state is created.

## Dependencies and integration points
The class integrates WebHDFS resource param classes with `Configuration`, `DFSConfigKeys`, `CommonConfigurationKeysPublic`, `FsPermission`, `AclEntry`, `XAttrCodec`, `XAttrSetFlag`, `Options.Rename`, `StorageType`, and `StringUtils`.

## Risks and edge cases
This file is a broad regression net for REST API surface syntax. It is sensitive to default HDFS block size, replication, and buffer-size configuration defaults. Static regex mutation can leak to other tests if a future assertion aborts before reset in the user-pattern test. Some invalid-value tests use try/catch rather than `assertThrows`, so a wrong exception type may not always be distinguished.

## Test signals
Passing confirms WebHDFS params reject malformed octal permissions, invalid booleans, bad ACL grammar, invalid FsAction strings, unknown HTTP ops, bad user names under default policy, and incorrectly encoded query strings. It also confirms defaults resolve from configuration where appropriate.
