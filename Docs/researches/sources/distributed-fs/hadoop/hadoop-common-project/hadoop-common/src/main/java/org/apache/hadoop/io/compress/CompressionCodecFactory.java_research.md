
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionCodecFactory.java

## Purpose
`CompressionCodecFactory` discovers and selects codecs by filename suffix, canonical class name, or short alias.

## Important APIs and Types
It holds a reversed-suffix `SortedMap<String, CompressionCodec>`, a name/alias map, and a canonical class-name map. Public APIs include `getCodecClasses`, `setCodecClasses`, constructor registration, `getCodec(Path)`, `getCodecByClassName`, `getCodecByName`, `getCodecClassByName`, `removeSuffix`, and a small CLI `main`.

## Control Flow
Discovery first loads `CompressionCodec` providers through Java `ServiceLoader`, then appends classes listed in `io.compression.codecs`, allowing configured classes to override by suffix when registered later. If no providers or configured classes exist, gzip and default deflate are registered. `getCodec(Path)` reverses and lowercases the filename, uses a head-map lookup, and selects the longest matching registered suffix.

## State and Persistence
Factory state is per-instance maps populated at construction. The static `ServiceLoader` is synchronized during iteration because it is lazy. Configuration is read but not otherwise persisted; `setCodecClasses` writes a comma-separated class list to `Configuration`.

## Dependencies and Integration
Depends on `CommonConfigurationKeys.IO_COMPRESSION_CODECS_KEY`, `ReflectionUtils`, `StringUtils`, `Path`, and `ServiceLoader`. It is the bridge between file naming conventions and codec instantiation for Hadoop readers and tools.

## Risks
Suffix registration assumes codec extensions are normalized enough for reverse-string matching; a codec returning an extension without a dot can still be registered but may behave unexpectedly. Misconfigured classes throw `IllegalArgumentException` during discovery. Because the maps contain instances, configuration changes after factory construction do not affect existing factories.

## Test Signals
`TestCodecFactory` validates default discovery, case-insensitive suffix matching, longest suffix matching, alias lookup, configured overrides, and parsing of comma-separated codec class names.
