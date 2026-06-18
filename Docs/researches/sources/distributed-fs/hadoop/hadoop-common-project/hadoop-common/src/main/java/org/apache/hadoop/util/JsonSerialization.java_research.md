# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/JsonSerialization.java

## Purpose

`JsonSerialization<T>` wraps Jackson serialization/deserialization for Hadoop objects, with helpers for local files, Hadoop filesystems, resources, bytes, strings, and pretty map writing.

## Important APIs, Types, And Functions

Static helpers are `writer()` and `mapReader()`. Instance APIs include `fromJson()`, `fromJsonStream()`, `load(File)`, `save(File,T)`, `fromResource()`, `fromInstance()`, `load(FileSystem,Path,FileStatus)`, `save(FileSystem,Path,T,boolean)`, `writeJsonAsBytes()`, `toBytes()`, `fromBytes()`, `toJson()`, and robust `toString(T)`.

## Control Flow, State, And Persistence

The constructor creates an `ObjectMapper` configured for unknown-property handling and indentation. Most mapper operations are synchronized. Local loads validate existence, file-ness, and non-empty content. Hadoop FS loads use `openFile()` with whole-file read policy and optional file status, then wrap JSON processing errors in `PathIOException`. Save methods overwrite only when requested and close streams in `finally`. Persistence is JSON written to local or Hadoop filesystems.

## Dependencies And Integration Points

It depends on Jackson, Hadoop `FileSystem`, `Path`, `FutureDataInputStreamBuilder`, `PathIOException`, `FutureIO.awaitFuture`, and annotations. It is reused by registry, REST, and configuration/state persistence code.

## Risks And Test Signals

UTF-8 is hard-coded through a string charset name. Shared `ObjectMapper` access is synchronized but callers can mutate the mapper returned by `getMapper()`. Tests should cover empty input, malformed JSON, unknown fields, filesystem status optimization, stream closure, overwrite false, resource loading, byte round trips, and robust `toString()` failure handling.
