# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/WebHdfsTestUtil.java

## Purpose
`WebHdfsTestUtil` is a small test helper for constructing WebHDFS/SWebHDFS clients, logging generated URLs, opening HTTP connections, parsing JSON responses, and converting WebHDFS delegation-token JSON into Hadoop token objects.

## Important APIs, types, and functions
- `createConf()` returns a new base `Configuration`.
- `getWebHdfsFileSystem(Configuration, String)` builds a URI from `DFS_NAMENODE_HTTP_ADDRESS_KEY` or `DFS_NAMENODE_HTTPS_ADDRESS_KEY` depending on scheme and returns a `WebHdfsFileSystem`.
- `getWebHdfsFileSystemAs(UserGroupInformation, Configuration[, String])` runs client construction inside a UGI `doAs`.
- `toUrl(WebHdfsFileSystem, HttpOpParam.Op, Path, Param...)` delegates to `webhdfs.toUrl` and logs the resulting URL.
- `openConnection`, `sendRequest`, `getAndParseResponse`, and `convertJsonToDelegationToken` wrap lower-level WebHDFS HTTP/JSON APIs.

## Control flow
The helper is stateless. Most methods are single-step factories or adapters: construct URI, call `FileSystem.get`, call `toUrl`, create a default `URLConnectionFactory`, connect, parse JSON, or convert token JSON.

## State and persistence behavior
No persistent state is stored except the static logger. `openConnection` creates a new connection factory with 60-second connect/read timeouts for each call.

## Dependencies and integration points
It sits between WebHDFS tests and `WebHdfsFileSystem`, `URLConnectionFactory`, `JsonUtilClient`, UGI, HDFS config keys, and WebHDFS resource parameter classes.

## Risks and edge cases
The overload `getWebHdfsFileSystemAs(ugi, conf, scheme)` ignores its `scheme` argument and always calls `getWebHdfsFileSystem(conf, WEBHDFS_SCHEME)`. That can mask intended SWebHDFS coverage if callers rely on the overload. `createConf()` is deliberately minimal and does not set NameNode addresses; callers must provide them.

## Test signals
The file itself contains no tests, but downstream tests use it to signal URL construction, live WebHDFS access, HTTP response parsing, and delegation-token JSON conversion behavior.
