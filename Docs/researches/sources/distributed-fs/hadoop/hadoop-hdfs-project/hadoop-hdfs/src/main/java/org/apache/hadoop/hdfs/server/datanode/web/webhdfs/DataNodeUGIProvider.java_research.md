# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/web/webhdfs/DataNodeUGIProvider.java

## Purpose

`DataNodeUGIProvider` builds and caches `UserGroupInformation` instances for DataNode WebHDFS requests. The DataNode uses these UGIs to execute DFSClient operations, while NameNode-side operations still perform authoritative authentication/authorization.

## Important APIs, Control Flow, and State

`init(Configuration)` creates a static Guava cache expiring entries after configured access time. `ugi()` first parses a delegation token. In secure mode with a token, it caches by token cache key and builds a token UGI by decoding `DelegationTokenIdentifier`, obtaining its user, and adding the token. Otherwise it builds a non-token UGI from `user.name` or the configured default web user, optionally wraps it as a proxy user from `doas`, and caches by `{remoteUser}` or `{remoteUser}:{doAs}`. `clearCache` clears the decoded delegation token identifier cache in secure test scenarios.

State is the static UGI cache and the per-request `ParameterParser`. There is no disk persistence, but cached UGIs can retain tokens and proxy-user identity until expiration.

## Dependencies, Integration, Risks, and Tests

Dependencies include `ParameterParser`, `JspHelper`, `UserGroupInformation`, delegation tokens, Guava cache, and DFS WebHDFS UGI cache config. It integrates with `WebHdfsHandler.channelRead0` before executing request operations under `ugi.doAs`.

Risks include static cache lifetime across DataNode reconfiguration/tests, cache key collisions if token/user representations change, proxy-user authorization being deferred, and insecure NameNode access to secure DataNode data being intentionally allowed when no token is present. Tests should cover secure token UGI, insecure/default web user UGI, proxy user creation, cache reuse/expiration, username validation, and logical URI token service handling through `ParameterParser`.
