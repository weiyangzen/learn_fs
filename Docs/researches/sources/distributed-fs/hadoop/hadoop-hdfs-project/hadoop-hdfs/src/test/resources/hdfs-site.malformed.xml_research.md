# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/hdfs-site.malformed.xml

## Purpose

`hdfs-site.malformed.xml` is a deliberately unusual HDFS configuration fixture for HDFS-7684. The complete 143-line file was read. Despite the name, the XML is structurally valid; the important malformed aspect is address values with leading and trailing whitespace so tests can verify trimming and URI/address parsing behavior.

## Important APIs, Types, and Functions

The file defines HDFS address keys such as `dfs.namenode.secondary.http-address`, `dfs.namenode.secondary.https-address`, `dfs.datanode.address`, `dfs.datanode.http.address`, `dfs.datanode.ipc.address`, `dfs.datanode.handler.count`, `dfs.namenode.http-address`, `dfs.datanode.https.address`, `dfs.namenode.https-address`, `dfs.namenode.backup.address`, `dfs.namenode.backup.http-address`, `dfs.journalnode.rpc-address`, `dfs.journalnode.http-address`, and `dfs.journalnode.https-address`. Consumers include HDFS address config helpers, NetUtils parsing, NameNode/DataNode/JournalNode HTTP/RPC server binding, and tests that load `hdfs-site.malformed.xml` as a resource.

## Control Flow

The fixture is loaded into a `Configuration`, then code under test reads each address string, trims whitespace where appropriate, parses host/port pairs, and builds socket addresses or HTTP/HTTPS endpoints. It includes values with trailing spaces and one backup HTTP address with leading and trailing spaces.

## State and Persistence Behavior

There is no persisted cluster state. The file influences transient service bind addresses and parsed endpoint values during configuration tests. The handler count of `10` is a normal numeric control value used to ensure non-address properties are still parsed correctly.

## Dependencies and Integration Points

It integrates with Hadoop XML configuration parsing, HDFS address-key constants, `NetUtils.createSocketAddr`, and any tests checking that URL/address strings are sanitized before server startup or URI display.

## Risks and Edge Cases

Risks include trimming regressions causing bind failures, preserving whitespace inside emitted URLs, treating leading whitespace as part of a hostname, and tests confusing this fixture with genuinely invalid XML. Address keys with secure/nonsecure variants make broad parser behavior visible across NameNode, DataNode, BackupNode, SecondaryNameNode, and JournalNode paths.

## Test Signals

Signals are successful parsing and service address resolution to expected host/port values such as `0.0.0.0:9870`, no `UnknownHostException` or number-format failures from whitespace, and tests proving rendered URLs do not include leading/trailing spaces.
