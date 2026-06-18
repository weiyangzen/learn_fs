<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/JspHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/JspHelper.java

## Purpose

`JspHelper` centralizes WebHDFS/JSP request identity handling: deriving the effective `UserGroupInformation`, decoding delegation tokens, applying proxy-user authorization, and honoring trusted proxy headers.

## Important APIs and types

Static APIs include `getDefaultWebUserName`, `getUGI` overloads, `getRemoteAddr`, `getRemotePort`, and `checkUsername`. Private helpers resolve NameNode service address, decode token-backed UGI, and parse `user.name` or legacy `ugi` query parameters.

## Control flow

In secure mode, `getUGI` prefers a delegation token parameter; token auth ignores `user.name` and `doAs`. Without a token, it requires servlet-filter authentication via `request.getRemoteUser`. In insecure mode, it uses `user.name`/`ugi` or the configured static web user. If a distinct `doAs` parameter is present, it creates a proxy UGI and calls `ProxyUsers.authorize` using `getRemoteAddr`. Token flow decodes the token, optionally sets service/kind from `nnaddr` or servlet context, verifies with a context `TokenVerifier`, obtains the token user, and attaches the token.

## State and persistence behavior

The helper is stateless. Request-derived tokens are attached to returned UGI instances. No persistent state is modified.

## Dependencies and integration points

It integrates servlet context/request APIs, `NameNodeHttpServer`, WebHDFS parameters, delegation tokens, `SecurityUtil`, `UserGroupInformation`, `ProxyUsers`, `ProxyServers`, and Kerberos short-name mapping.

## Risks and edge cases

Trusted `X-Forwarded-For` is honored only when the immediate remote address is in `ProxyServers`; stale proxy-server config affects audit/proxy checks. Token auth bypasses query user/doAs by design. Missing remote user in secure mode is fatal. `checkUsername` compares expected short names after Kerberos name translation.

## Test signals

Tests should cover secure token, secure filter user, insecure static user, `doAs` authorization, trusted and untrusted proxy headers, `nnaddr` token service setting, token verifier invocation, legacy `ugi`, and username short-name checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/JspHelper.java -->
