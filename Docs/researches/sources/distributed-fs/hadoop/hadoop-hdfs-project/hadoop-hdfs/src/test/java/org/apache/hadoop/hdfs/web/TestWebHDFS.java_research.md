# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFS.java

Purpose: broad slow integration suite for WebHDFS client/server behavior across file I/O, REST responses, snapshots, erasure coding, quotas, storage policies, retries, symlinks, trash, statistics, and compatibility.

Important APIs/types/functions: `MiniDFSCluster`, `WebHdfsTestUtil`, `WebHdfsFileSystem`, `DistributedFileSystem`, `DFSTestUtil`, `SnapshotTestHelper`, `HdfsAdmin`, `StoragePolicySatisfier`, `WebHdfsInputStream`, REST params `LengthParam`, `OffsetParam`, `NoRedirectParam`, JSON helpers, `RetryPolicy`.

Control flow: each test starts a cluster and `tearDown` shuts it down. Early tests write/read a 200 MiB file with seek and positional read verification, test NameNode restart retry, large paginated directory listing with non-superuser UGI, file-space quota failure, customized username/ACL regexes, no-datanode create failure, invalid path REST error, snapshot allow/disallow/create/delete/rename/diff/listing, EC file status flags and EC policy commands, insecure delegation token fallback behavior, offset/length HTTP open, content summary and quota usage/setters, pread/stream mixing, home directory per user, block locations via API and raw REST, read retry classification with spies, `noredirect=true` location JSON and CORS, trash roots including snapshot and encryption zone cases, storage policy operations and disabled-policy error, external SPS behavior, append failure with insufficient DNs, fs server defaults and backward compatibility, exception cause propagation, WebHDFS statistics counters, symlink target/status, filesystem status, EC policy/codecs listing, and multi-user trash roots.

State and persistence behavior: heavy MiniDFSCluster filesystem state, global static `cluster`, randomized file contents, UGI login-user mutation in one test, external SPS lifecycle, key-provider test file for encryption zones, and raw HTTP connections.

Dependencies and integration points: covers most WebHDFS public API and REST surface, comparing many results against `DistributedFileSystem` as oracle. It integrates NameNode web resources, DataNode redirects, HDFS client retry policy, EC, snapshots, quotas, storage policies, encryption-zone trash, and statistics.

Risks: broad and slow; several tests use randomness, large I/O, raw HTTP, sleeps/retries, global cluster state, and external services. Some helper assertions compare JSON/objects manually and can be sensitive to protocol shape. The EC normal-file check appears to fetch `normalDir` status while comparing `normalFile` expectations, which is worth rechecking if that test changes.

Test signals: end-to-end WebHDFS parity with DFS APIs, REST status/error codes, redirect/noredirect behavior, retry/no-retry decisions, metadata serialization, and feature-specific regressions.
