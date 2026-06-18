
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DeflateCodec.java

## Purpose
`DeflateCodec` is an alias subclass of `DefaultCodec` that enables discovery by the `deflate` codec name/class while preserving the same implementation.

## Important APIs and Types
It declares no methods or state and inherits all behavior from `DefaultCodec`.

## Control Flow
All stream creation, type lookup, compression, decompression, pooling, and extension behavior are inherited unchanged.

## State and Persistence
No local state exists. Inherited state is the `DefaultCodec` configuration.

## Dependencies and Integration
It integrates with `CompressionCodecFactory` class-name and alias lookup. Configurations can list `org.apache.hadoop.io.compress.DeflateCodec` to distinguish the alias from `DefaultCodec`.

## Risks
Because `getDefaultExtension()` is inherited, both default and deflate aliases map to `.deflate`; registering both in a factory can cause last-registration-wins behavior for that suffix.

## Test Signals
`TestCodecFactory` validates discovery of `DeflateCodec` by class/name in configured factories.
