# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsFileSystemContract.java

Purpose: WebHDFS implementation of the generic filesystem contract plus direct REST edge-case tests.

Important APIs/types/functions: `FileSystemContractBaseTest`, static `MiniDFSCluster`, `WebHdfsTestUtil.getWebHdfsFileSystemAs`, `WebHdfsFileSystem.toUrl`, REST params (`LengthParam`, `OffsetParam`, `DoAsParam`, `NamenodeAddressParam`), `WebHdfsTestUtil.sendRequest/getAndParseResponse`.

Control flow: a static two-datanode cluster starts once and root permissions are opened. Each test uses a non-superuser WebHDFS client. Tests validate mkdir failure below files, block-location parity with DFS, case-insensitive `op` query handling, missing file open errors, seek and positional reads, root path behavior, `OPEN` length/offset truncation to actual content, many HTTP response codes and content types, bad doAs, empty set-owner/permission params, append, missing `namenoderpcaddress` on DN create redirect, JSON parse failure on non-JSON content, create paths with spaces, datanode create redirects missing optional params, and `access` permission/not-found behavior.

State and persistence behavior: persistent static cluster state across methods, per-test non-superuser UGI, files under `/test` and permission changes.

Dependencies and integration points: generic filesystem contract, WebHDFS URL generation, raw HTTP requests, NameNode/DataNode two-step create, access-control checks, and block-location JSON path.

Risks: static cluster has no explicit class teardown in this file, so lifecycle depends on test framework/JVM cleanup. Raw URL string manipulation is sensitive to parameter ordering and encoding. Case-insensitive op test notes Jersey2 URL-change support caveat.

Test signals: contract parity, raw REST response codes, redirect parameter handling, range reads, permissions, and block-location equivalence.
