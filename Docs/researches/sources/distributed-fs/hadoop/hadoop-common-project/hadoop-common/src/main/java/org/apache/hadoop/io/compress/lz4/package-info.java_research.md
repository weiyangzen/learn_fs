# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/lz4/package-info.java

Purpose: package-level documentation for Hadoop's LZ4 compression/decompression implementation.

Important APIs and control flow: no executable code; provides Javadoc link to LZ4 and marks the package as `Private` and `Unstable`.

State and persistence: no runtime state.

Dependencies and integration: classification annotations integrate with Hadoop's compatibility policy. The package contains `Lz4Compressor` and `Lz4Decompressor` implementations used by Hadoop compression codecs.

Risks and test signals: compile/Javadoc checks are enough. Any annotation change affects API compatibility expectations.
