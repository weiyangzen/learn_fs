<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/hdfs_configuration.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/hdfs_configuration.cc

## Purpose
Implements HDFS-specific interpretation of generic Hadoop configuration into libhdfspp `Options`, including default resource names, HA nameservice parsing, authentication mode, timeouts, retries, failover limits, default filesystem, and block size.

## Important APIs, Types, And Functions
`HdfsConfiguration::GetDefaultFilenames()` adds `hdfs-site.xml` to `core-site.xml`. Helpers include `OptionalSet`, `SplitOnComma`, `RemoveSpaces`, `PrependHdfsScheme`, and `LookupNameService`. `GetOptions()` is the main exported behavior.

## Control Flow
`GetOptions()` starts from default `Options`, overlays known numeric/URI keys, parses `dfs.nameservices`, and for each service reads `dfs.ha.namenodes.<service>` plus `dfs.namenode.rpc-address.<service>.<node>`. Missing schemes are prefixed with `hdfs://`. Authentication is mapped to Kerberos only when the configured value matches `kerberos`; otherwise simple auth is used.

## State And Persistence
The object is an immutable config snapshot. Derived `Options` is a new value containing HA service maps and scalar settings. No files are written.

## Dependencies And Integration Points
Depends on `Configuration`, `Options`, `NamenodeInfo`, `URI`, and logging. It feeds `FileSystem::New`, C builder connection paths, and HA failover code.

## Risks
Only selected Hadoop keys are honored. HA parse failures clear the nameservice list and log errors rather than returning a structured failure. `RemoveSpaces` removes only literal spaces, not other whitespace. Multiple nameservices are parsed, but downstream behavior must still choose the correct service. Authentication values other than exact Kerberos fall back to simple.

## Test Signals
Tests should cover default-only options, every supported key, HA service parsing with multiple namenodes and missing keys, scheme prefixing, whitespace in namenode lists, Kerberos/simple auth values, and malformed RPC address URIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/hdfs_configuration.cc -->
