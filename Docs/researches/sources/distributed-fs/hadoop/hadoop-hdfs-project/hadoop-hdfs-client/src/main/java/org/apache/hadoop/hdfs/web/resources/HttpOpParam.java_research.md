# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/HttpOpParam.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/HttpOpParam.java` is part of the Hadoop HDFS client WebHDFS resource-parameter layer. It was read as a complete 134-line source file for this work item. Its specific role is shared base for WebHDFS HTTP operation parameters. These classes convert REST query text into typed Java values before WebHDFS servlet/client code maps the request to HDFS RPCs.

## Important APIs, Types, and Functions

Local declarations: `HttpOpParam`. Important local methods/constructors include `getType`, `getRequireAuth`, `getDoOutput`, `getRedirect`, `getExpectedHttpResponseCode`, `toQueryString`, `valueOf`, `IllegalArgumentException`, `TemporaryRedirectOp`, `getValueString`, `HttpOpParam`, `super`. The core behavior is `Type`, `Op` interface, and `TemporaryRedirectOp` wrapper for CREATE, APPEND, OPEN, and GETFILECHECKSUM.

## Control Flow

The normal flow is request/query construction, subclass constructor normalization, `Domain.parse` validation or conversion, optional range checking in numeric bases, then later `getValue()`, `getValueString()`, `toString()`, or op metadata access by WebHDFS code. The file has no background execution; all behavior happens synchronously while building or decoding a request parameter.

## State and Persistence Behavior

State is in-memory only: each parameter instance holds its parsed value and a shared immutable or effectively static domain object. There is no file, network, or durable persistence here. Static domains are process-wide; this matters most for `UserParam`, whose pattern domain can be replaced for tests/configuration.

## Dependencies and Integration Points

Direct dependency signals from imports: `Arrays`, `Collections`, `List`, `Response`. The package integrates with WebHDFS operation dispatch, JAX-RS resource parsing, HDFS protocol classes such as permissions/quotas/xattrs, and query-string construction consumed by WebHDFS clients and servers.

## Risks and Edge Cases

Temporary redirects change the expected status to HTTP 307 and suppress output while preserving the underlying query string. Cross-version compatibility depends on keeping parameter names, defaults, and string encodings stable because they are visible WebHDFS API surface. Null/default normalization is subtle: several empty-string defaults intentionally become Java `null`, while cursor-like parameters may preserve an empty string.

## Test Signals

Relevant tests should cover valid and invalid query values, default/null normalization, range boundaries, string rendering, and WebHDFS end-to-end operations using this parameter. Op parameters also need tests for expected HTTP status, redirect decisions, auth-required flags, and invalid operation messages.
