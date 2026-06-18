<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/TokenVerifier.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/TokenVerifier.java

## Purpose

`TokenVerifier` is the WebHDFS delegation-token verification extension point used by NameNode and Router HTTP helpers.

## Important APIs and types

It is generic over `AbstractDelegationTokenIdentifier` and declares `verifyToken(T t, byte[] password) throws IOException`.

## Control flow

`JspHelper` decodes a delegation token from the request, reads the identifier, obtains a verifier from servlet context, and calls `verifyToken` with the identifier and token password before accepting token-backed UGI.

## State and persistence behavior

The interface owns no state. Implementations validate against token secret managers or router-side token services.

## Dependencies and integration points

It integrates with WebHDFS, `JspHelper`, `NameNodeHttpServer`, delegation-token identifiers, and NameNode/Router token verification.

## Risks and edge cases

If no verifier is present in context, `JspHelper` accepts the decoded token UGI without this callback. Implementations must avoid leaking token secrets in exception messages or logs.

## Test signals

Tests should cover successful verification, rejected password/identifier, missing verifier behavior, Router/NameNode implementations, and propagation of `IOException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/TokenVerifier.java -->
