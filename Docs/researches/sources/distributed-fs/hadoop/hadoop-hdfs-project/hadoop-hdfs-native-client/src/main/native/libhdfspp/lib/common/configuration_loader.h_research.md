<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader.h

## Purpose
Declares the templated `ConfigurationLoader` API for creating, loading, overlaying, and validating typed `Configuration` subclasses.

## Important APIs, Types, And Functions
The public template methods are `NewConfig`, `Load`, `LoadFromStream`, `LoadFromFile`, `OverlayResourceString`, `OverlayResourceStream`, `OverlayResourceFile`, `OverlayValue`, `LoadDefaultResources`, and `ValidateDefaultResources`. Search-path methods manage the loader's directory list. Protected methods update maps from files, streams, strings, bytes, or individual values.

## Control Flow
Template definitions are included from `configuration_loader_impl.h`, while non-template path and XML parsing logic is implemented in `configuration_loader.cc`.

## State And Persistence
`search_path_` is mutable loader state. Generated configurations receive copied maps; persistence is external to this class.

## Dependencies And Integration Points
This header is the construction gateway for `Configuration` and `HdfsConfiguration` because those constructors are protected/friend-only.

## Risks
Template users can instantiate the loader for subclasses that do not follow the expected constructor/static method contract, leading to compile errors. Search path mutation is not synchronized, so loaders should not be mutated concurrently.

## Test Signals
Build tests should instantiate all template methods for `Configuration` and `HdfsConfiguration`; behavior tests should verify overlay and validation results against concrete XML fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader.h -->
