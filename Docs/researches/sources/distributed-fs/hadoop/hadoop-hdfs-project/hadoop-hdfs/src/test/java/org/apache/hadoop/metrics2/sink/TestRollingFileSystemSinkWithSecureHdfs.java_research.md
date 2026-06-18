# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSinkWithSecureHdfs.java

## Purpose
This class tests `RollingFileSystemSink` with Kerberos-secured HDFS, HTTPS-only HTTP policy, block tokens, and data-transfer protection. It verifies that a correctly configured sink principal can write metrics and that missing sink principal/keytab settings are reported as initialization errors.

## Important APIs, types, and functions
- `initKdc()` starts a `MiniKdc` and creates sink and HDFS/SPNEGO principals with keytabs.
- `initCluster()` creates a secure HDFS config, installs it into `RollingFileSystemSink.suppliedConf`, starts a four-DataNode MiniDFSCluster, and calls `createDirectoriesSecurely()`.
- `createDirectoriesSecurely()` logs in as HDFS to create `/tmp` with `0777`, logs in as sink to create `/tmp/test`, and supplies the sink-authenticated `FileSystem` to `RollingFileSystemSink`.
- `createSecureConfig(String)` sets Kerberos principals, keytabs, block tokens, data-transfer QOP, HTTPS addresses, SASL retry count, null group mapping, and SSL keystore resources.

## Control flow
Class setup starts KDC once. Per-test setup starts a secure cluster and prepares writable directories. `testWithSecureHDFS` initializes the metrics system with principal/keytab settings and runs the inherited write test inside `sink.doAs`. `testMissingPropertiesWithSecureHDFS` omits required principal/keytab properties and asserts `MockSink.errored`. Per-test cleanup shuts down the cluster and resets UGI and static sink-supplied configuration/filesystem.

## State and persistence behavior
The test writes KDC databases, keytabs, SSL config files, and HDFS directories. Static fields hold principal names and keytab paths. `RollingFileSystemSink.suppliedConf` and `suppliedFilesystem` are global test hooks reset after each test. KDC is stopped after all tests.

## Dependencies and integration points
It integrates MiniKdc, secure MiniDFSCluster, HDFS Kerberos keytab login, SPNEGO configuration, SSL keystore test utilities, metrics2, `NullGroupsMapping`, and `RollingFileSystemSinkTestBase`.

## Risks and edge cases
The test is environment-sensitive because it uses Kerberos, localhost principals, SSL resources, and secure data transfer. Static sink hooks must be reset or they can affect other rolling-sink tests. It covers a basic write as a proxy for more complex sink operations rather than retesting append and failure cases under security.

## Test signals
Passing confirms that the sink can authenticate and write to secure HDFS with supplied config/filesystem, and that secure clusters reject incomplete sink authentication configuration by marking the sink errored.
