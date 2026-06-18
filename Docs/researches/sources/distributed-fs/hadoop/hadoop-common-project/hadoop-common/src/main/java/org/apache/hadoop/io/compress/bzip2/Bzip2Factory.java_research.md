
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/Bzip2Factory.java

## Purpose
`Bzip2Factory` centralizes selection between native bzip2 compressor/decompressor implementations and pure-Java dummy placeholders.

## Important APIs and Types
Static APIs include `isNativeBzip2Loaded`, `getLibraryName`, compressor/decompressor type and instance factories, and configuration helpers for block size and work factor.

## Control Flow
`isNativeBzip2Loaded(conf)` reads `io.compression.codec.bzip2.library`, resets cached load state when the library name changes, uses pure Java immediately for `java-builtin`, and otherwise attempts native symbol initialization if Hadoop native code is loaded. Failures log a warning and fall back to pure Java. Factory methods branch on cached native availability.

## State and Persistence
Static state stores the last requested bzip2 library name and whether native bzip2 loaded. Configuration keys for block size/work factor are stored in `Configuration`, not globally persisted.

## Dependencies and Integration
Depends on `NativeCodeLoader`, `Bzip2Compressor`, `Bzip2Decompressor`, dummy classes, and SLF4J. `BZip2Codec` calls it for all native-vs-Java decisions.

## Risks
Load state is static and keyed only by library name, so changing configurations in the same JVM intentionally resets load state but still shares state across users. Native initialization catches `Throwable`, which favors fallback availability over surfacing native problems. Pure-Java mode exposes dummy compressor/decompressor types for interface compatibility.

## Test Signals
`TestCommonConfigurationFields` references the config keys. `TestBzip2CompressorDecompressor` uses `assumeTrue(Bzip2Factory.isNativeBzip2Loaded(...))` to gate native tests. BZip2 codec tests cover Java fallback stream behavior.
