# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestHttpFSAccessControlled.java

## Purpose
`TestHttpFSAccessControlled` verifies the `httpfs.access.mode` server setting gates read and write HTTP operations as intended.

## Important APIs, Types, and Functions
`startMiniDFS` creates a hand-rolled `MiniDFSCluster` with permissions enabled and ACL support intentionally not enabled. `createHttpFSServer` writes separate HDFS and HttpFS config files, including `httpfs.hadoop.config.dir`, proxy-user settings, and auth secret, then starts Jetty with the webapp. Helper methods `getCmd`, `putCmd`, `postCmd`, and `deleteCmd` build raw `/webhdfs/v1/...` URLs and assert HTTP 200 or 403.

## Control Flow
The single test `testAcessControlledFS` creates three files, retrieves the running `HttpFSServerWebApp` config, and mutates `httpfs.access.mode` through `read-write`, `write-only`, and `read-only`. It then verifies GETFILESTATUS/LISTSTATUS always pass, GETXATTRS is forbidden in write-only, and SETPERMISSION/UNSETSTORAGEPOLICY/DELETE are forbidden in read-only but allowed in write-capable modes.

## State and Persistence
The test starts a MiniDFSCluster, writes temporary XML configuration and secret files, creates HDFS files, mutates live HttpFS configuration, and shuts down the cluster at the end.

## Dependencies and Integration Points
It integrates access-control mode configuration from `httpfs-default.xml`, the running `HttpFSServerWebApp` service/config registry, raw HttpURLConnection behavior, authentication with simple `user.name`, and HTTP method/operation dispatch.

## Risks
The test mutates global live config and resets access mode to read-write before shutdown; failures before reset could affect later tests if the same server survived. The method name has a typo (`testAcessControlledFS`). It verifies a representative operation set rather than every operation in each mode.

## Test Signals
This is the direct regression signal for read-write, write-only, and read-only enforcement. It confirms the documented exception that write-only still permits `GETFILESTATUS` and `LISTSTATUS`.
