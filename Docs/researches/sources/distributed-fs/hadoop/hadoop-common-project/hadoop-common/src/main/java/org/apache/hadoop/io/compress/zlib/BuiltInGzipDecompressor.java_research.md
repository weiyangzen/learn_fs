# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/zlib/BuiltInGzipDecompressor.java

Purpose: pure-Java gzip `Decompressor` that parses gzip members manually and delegates raw deflate bytes to `java.util.zip.Inflater`, marked `@DoNotPool`.

Important APIs and control flow: `setInput()` stores the caller buffer without copying. `decompress()` drives a state machine: parse basic/optional header fields, feed remaining bytes to `Inflater`, update CRC with produced output, rewind unconsumed trailer bytes from `Inflater.getRemaining()`, parse CRC and size trailer, and enter `FINISHED`. `needsInput()` is special: while not in `FINISHED`, it may ask for more input even outside the deflate stream. `getRemaining()` reports bytes after the current gzip member.

State and persistence: state includes `GzipStateLabel`, `Inflater`, user buffer offsets, a small local header/trailer buffer, CRC, header/trailer byte counters, and flags for optional fields. `reset()` clears the member parser; `end()` closes the inflater and sets `ENDED`.

Dependencies and integration: implements Hadoop `Decompressor`; depends on Java `Inflater`, `DataChecksum`, `AlreadyClosedException`, and gzip RFC layout. It is used when native zlib is unavailable or when a built-in gzip codec path is selected.

Risks and test signals: test basic gzip, optional filename/comment/extra/header-CRC fields, concatenated member leftover handling, one-byte input buffers, CRC/size failures, and calls after `end()`. The state machine depends on caller preserving input until `needsInput()` says it is safe.
