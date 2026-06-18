# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterWebHdfsMethods.java

Purpose: validates WebHDFS create handling through the Router, namespace selection from mount tables, datanode network-location namespace parsing, and invalid path error conversion.

Important APIs/types/functions: `StateStoreDFSCluster`, `RouterConfigBuilder`, `RouterContext`, `RouterWebHdfsMethods`, `WebHdfsFileSystem.jsonParse`, `DestinationOrder`, `FederationTestUtils.createMountTableEntry`, `HttpURLConnection`, `FileSystem`, and `Path`. `globalSetUp()` starts a two-nameservice state-store cluster with RPC, HTTP, and admin services and records the router HTTP URI.

Control flow: `testWebHdfsCreate()` sends an HTTP `PUT` to `/webhdfs/v1/tmp/file?op=CREATE&user.name=<user>` and expects HTTP 201, then checks the file exists only in the default `ns0`. `testWebHdfsCreateWithMounts()` installs a mount point to `ns1`, creates through WebHDFS, and verifies placement only in `ns1`. `testGetNsFromDataNodeNetworkLocation()` checks namespace extraction from rack paths. `testWebHdfsCreateWithInvalidPath()` sends duplicated slashes and expects HTTP 400 with `InvalidPathException` in the parsed JSON response.

State and persistence behavior: mount-table state affects HTTP routing and physical NN file creation. The suite relies on the shared cluster shutdown for cleanup. Dependencies include router HTTP endpoints, WebHDFS request parsing, mount resolution, and namenode file status checks. Risks include real socket timing, local username query parameters, and state leakage from created files or mount entries. Test signals are HTTP response codes, parsed remote exception class names, and per-namespace file existence.
