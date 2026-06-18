# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/delegation/DelegationTokenSelector.java

## Purpose

`DelegationTokenSelector.java` selects HDFS delegation tokens, including from non-HDFS filesystems such as WebHDFS that need to map a URI-facing service to the NameNode RPC token service.

## Important APIs, Types, and Functions

The class extends `AbstractDelegationTokenSelector<DelegationTokenIdentifier>`, declares `SERVICE_NAME_KEY = "hdfs.service.host_"`, has a constructor fixed to `HDFS_DELEGATION_KIND`, and provides `selectToken(URI nnUri, Collection<Token<?>> tokens, Configuration conf)`.

## Control Flow

The URI-based selector builds an initial token service from the URI, checks configuration key `hdfs.service.host_<service>` for an override host/port, defaults to `DFS_NAMENODE_RPC_PORT_DEFAULT`, rebuilds the token service using the original URI host and resolved RPC port, and delegates to the superclass `selectToken(Text, tokens)`.

## State and Persistence Behavior

The selector is stateless. Configuration can supply per-service host/port overrides but no state is stored in the object.

## Dependencies and Integration Points

Dependencies include `Configuration`, `HdfsClientConfigKeys`, `SecurityUtil`, `NetUtils`, URI, Hadoop tokens, and delegation token selector base class. It integrates with WebHDFS and other clients that acquire or search HDFS delegation tokens without directly using the NameNode RPC URI.

## Risks and Edge Cases

The code intentionally avoids resolving the original URI hostname when building the final service. Misconfigured `hdfs.service.host_*` values can select the wrong port and fail to find a token. It assumes the remote cluster RPC port matches local defaults unless configured. Null URI host, null token collections, or missing configuration can surface through lower-level utilities.

## Test Signals

Tests should cover default RPC-port selection, configured service host overrides, preservation of original hostname, token match/miss behavior, WebHDFS URI examples, and malformed override addresses.
