# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/ZlibDecompressor.java

Purpose: native Hadoop zlib `Decompressor` with array and direct-buffer decompression paths and configurable header detection.

Important APIs and control flow: static initialization mirrors `ZlibCompressor`. `setInput()` stores caller bytes and copies up to the direct buffer. `needsInput()` drains uncompressed output, reloads saved compressed input, or asks for more. `decompress()` drains pending output, rewinds output direct buffer, calls native `inflateBytesDirect()`, and returns available bytes. `getRemaining()` combines saved user input with native remaining bytes. `inflateDirect()` temporarily points instance buffers at caller direct buffers and advances source based on native-consumed offsets.

State and persistence: stores native `stream`, header mode, compressed/uncompressed direct buffers, compressed offsets/lengths, user input offsets, `finished`, and `needDict`. `reset()` clears native and Java state; `end()` releases native stream; `finalize()` calls `end()`.

Dependencies and integration: implements Hadoop `Decompressor`; nested `ZlibDirectDecompressor` implements `DirectDecompressor`. Used by `ZlibFactory` for native zlib and direct decompression.

Risks and test signals: cover dictionary-needed streams, autodetect gzip/zlib mode, direct decompressor nonzero positions, concatenated/post-stream remaining bytes, reset after corrupt data, and closed-stream access. JNI/native state and direct buffer mutation are the key correctness risks.
