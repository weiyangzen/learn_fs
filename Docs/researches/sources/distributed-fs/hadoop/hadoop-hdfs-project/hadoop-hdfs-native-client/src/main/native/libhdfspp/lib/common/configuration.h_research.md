<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration.h

## Purpose
Declares the `Configuration` class and its protected storage contract for Hadoop-style XML configuration data.

## Important APIs, Types, And Functions
The header exposes typed getters, protected `ConfigData`, `ConfigMap`, constructors used by `ConfigurationLoader`, `GetDefaultFilenames`, `raw_values_`, and `fixCase`. It also defines `hdfs::optional<T>` as `std::experimental::optional<T>`.

## Control Flow
Runtime control flow is implemented in `configuration.cc`; this header defines the read-only public surface and grants `ConfigurationLoader` friend access to construct populated instances.

## State And Persistence
`raw_values_` stores all parsed properties. The comments document the intended immutable/thread-safe model after construction.

## Dependencies And Integration Points
Used by `ConfigurationLoader`, `HdfsConfiguration`, `ConfigParser`, and C builder configuration APIs.

## Risks
Because `raw_values_` is non-const for copyability and protected for loader/subclass construction, immutability is by convention. New subclasses must preserve that contract.

## Test Signals
Compile tests should verify loader friendship and subclass construction; behavior tests live with `configuration.cc` and loader overlays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration.h -->
