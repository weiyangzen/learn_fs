# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/SWebHdfsFileSystem.java

## Purpose

`SWebHdfsFileSystem` is the HTTPS variant of `WebHdfsFileSystem`.

## Important APIs, Types, And Functions

It overrides `getScheme` to return `swebhdfs`, `getTransportScheme` to return `https`, `getTokenKind` to return `SWEBHDFS delegation`, and `getDefaultPort` to return the configured HDFS NameNode HTTPS default.

## Control Flow

All filesystem behavior remains in `WebHdfsFileSystem`; this subclass changes URI scheme, transport, token kind, and default port selection during initialization and URL construction.

## State And Persistence

It adds no state and no persistence.

## Dependencies And Integration Points

It integrates with Hadoop `FileSystem` scheme resolution, WebHDFS token management, SSL connection configuration, and `HdfsClientConfigKeys.DFS_NAMENODE_HTTPS_PORT_DEFAULT`.

## Risks

Wrong scheme/token-kind pairing would break token selection and renewals. HTTPS relies on correct SSL configuration from the inherited connection factory path.

## Test Signals

Tests should initialize `swebhdfs://` URIs, verify HTTPS URLs/default ports, and validate SWEBHDFS delegation-token selection and renewal.
