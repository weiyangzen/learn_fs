# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/GetGroups.java`

## Purpose

`GetGroups` is the HDFS-specific implementation of the generic `GetGroupsBase` tool. It prints group memberships for one or more users by contacting the NameNode's `GetUserMappingsProtocol`.

## Important APIs, Types, and Functions

- Static initialization loads `HdfsConfiguration`.
- `getProtocolAddress` returns the NameNode address from `DFSUtilClient.getNNAddress`.
- `setConf` wraps config in `HdfsConfiguration`, sets the service principal to the NameNode Kerberos principal, and delegates to the base class.
- `getUgmProtocol` creates a NameNode proxy for `GetUserMappingsProtocol`.
- `main` handles help and uses `ToolRunner`.

## Control Flow

The inherited `GetGroupsBase` handles argument iteration and printing. This subclass supplies HDFS address/proxy construction and security configuration. The tool starts in `main`, exits early for help, then runs against a new `HdfsConfiguration`.

## State and Persistence Behavior

The tool is read-only. It mutates only its local configuration copy to set the server principal key, then performs NameNode RPCs.

## Dependencies and Integration Points

It integrates with `GetGroupsBase`, `GetUserMappingsProtocol`, `NameNodeProxies`, `DFSUtilClient`, `FileSystem.getDefaultUri`, HDFS Kerberos config keys, and `ToolRunner`.

## Risks and Edge Cases

- It depends on default filesystem/NameNode resolution; incorrect `fs.defaultFS` or HA config causes proxy failures.
- Security principal configuration must match the NameNode service or Kerberos RPC authentication fails.
- Behavior for no usernames is inherited and should be checked at base-class level.

## Test Signals

Tests should verify principal injection, correct protocol address, proxy creation configuration, help handling, output stream injection, and behavior against mocked user mapping protocol.
