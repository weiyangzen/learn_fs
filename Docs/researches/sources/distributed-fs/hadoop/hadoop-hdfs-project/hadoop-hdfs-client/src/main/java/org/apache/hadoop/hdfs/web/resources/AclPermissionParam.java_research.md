# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/AclPermissionParam.java

## Purpose

`AclPermissionParam` serializes and parses the `aclspec` WebHDFS parameter for ACL operations.

## Important APIs, Types, And Functions

It extends `StringParam`, defines mutable static `DOMAIN`, constructors from string and `List<AclEntry>`, test hooks `getAclPermissionPattern`, `setAclPermissionPattern`, parser `getAclPermission`, and helper `parseAclSpec`.

## Control Flow

Strings equal to empty default become null. ACL entry lists are converted to comma-separated stable ACL entry strings. Parsing delegates to `AclEntry.parseAclSpec` with caller-selected permission inclusion.

## State And Persistence

The static domain/pattern is mutable process-wide and initialized from the default HDFS client ACL regex. Individual params store parsed string values only.

## Dependencies And Integration Points

`WebHdfsFileSystem.initialize` can replace the pattern from configuration. ACL mutation methods use this parameter.

## Risks

Global mutable regex affects all clients in the JVM. Constructor from list calls `parseAclSpec` twice. Null entries serialize as empty components, which can be surprising.

## Test Signals

Tests should cover configured regex, empty/null ACLs, multiple entries, includePermission parsing, invalid specs, and process-wide pattern reset.
