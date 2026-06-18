<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader_impl.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader_impl.h

## Purpose
Provides the inline template implementations for `ConfigurationLoader`. It converts parsed `ConfigMap` copies into typed configuration objects and implements the generic overlay/default-resource logic.

## Important APIs, Types, And Functions
Defines `NewConfig`, `Load`, `LoadFromStream`, `LoadFromFile`, `OverlayResourceFile`, `OverlayResourceStream`, `OverlayResourceString`, `OverlayValue`, `LoadDefaultResources`, and `ValidateDefaultResources`.

## Control Flow
Each overlay method copies `src.raw_values_`, updates the copy from a source, and returns an optional `T` only on success. Default-resource loading iterates `T::GetDefaultFilenames()` and succeeds if any resource updates the map. `OverlayValue` always returns a config after attempting to update one value.

## State And Persistence
No independent state exists; it operates on loader search paths and local map copies. Output configs are in-memory snapshots.

## Dependencies And Integration Points
Included at the bottom of `configuration_loader.h`, so all template logic is visible to translation units using the loader.

## Risks
`OverlayValue` ignores the boolean result from `UpdateMapWithValue`, so attempts to override a final key silently return an unchanged map. Default-resource loading treats partial success as success, which is correct for Hadoop layering but can hide missing secondary resources unless validation is called.

## Test Signals
Tests should assert optional empty results for invalid resources, final-value overlay behavior, default-resource partial loading, and direct key overlay semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader_impl.h -->
