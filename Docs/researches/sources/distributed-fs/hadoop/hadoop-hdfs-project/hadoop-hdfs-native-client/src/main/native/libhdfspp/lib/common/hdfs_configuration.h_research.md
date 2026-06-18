<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/hdfs_configuration.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/hdfs_configuration.h

## Purpose
Declares `HdfsConfiguration`, the HDFS-specific subclass of `Configuration` that converts Hadoop XML properties into libhdfspp runtime `Options`.

## Important APIs, Types, And Functions
The public API is `Options GetOptions()`. The header declares constants for supported keys such as `fs.defaultFS`, socket/connect retry timeouts, authentication, block size, and failover limits. Private constructors are friend-only for `ConfigurationLoader`, and `LookupNameService` handles HA service expansion.

## Control Flow
Implementation in `hdfs_configuration.cc` reads the inherited property map and constructs `Options`.

## State And Persistence
State is inherited `raw_values_`. The class is intended as an immutable parsed configuration snapshot.

## Dependencies And Integration Points
Used by the C builder, `ConfigParser`, and filesystem construction. It is the bridge from Hadoop config naming to libhdfspp option names.

## Risks
Adding supported Hadoop keys requires changes in both this header and implementation. Constructor privacy means new loaders/tests must use `ConfigurationLoader`.

## Test Signals
Compile tests should confirm loader instantiation, and behavior tests should verify every declared key affects `Options` as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/hdfs_configuration.h -->
