# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInZlibInflater.java

Purpose: wrapper that adapts Java `Inflater` to Hadoop's `Decompressor` interface for non-native zlib decompression.

Important APIs and control flow: constructors mirror `Inflater`; `decompress()` delegates to `inflate()` and converts `DataFormatException` to `IOException`.

State and persistence: all stream state is inherited from `Inflater`; no additional fields or persistence.

Dependencies and integration: selected by `ZlibFactory` when native zlib is unavailable. It participates in Hadoop's decompressor pool through the standard `Decompressor` API.

Risks and test signals: cover invalid compressed data error conversion, `nowrap` behavior, reset/end lifecycle inherited from `Inflater`, and parity with native `ZlibDecompressor` for common streams.
