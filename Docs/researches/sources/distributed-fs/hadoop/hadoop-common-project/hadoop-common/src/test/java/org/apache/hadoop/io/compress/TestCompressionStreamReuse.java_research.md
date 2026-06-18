<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressionStreamReuse.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressionStreamReuse.java

Purpose: Tests whether compression output streams can be reset and reused for fresh compressed members across BZip2, Gzip, and ZStandard codecs.

Important APIs/types/functions: public tests call `resetStateTest` for `BZip2Codec`, `GzipCodec`, `ZStandardCodec`, and Gzip with zlib compression level/strategy parameters. `resetStateTest` uses `RandomDatum.Generator`, `CompressionOutputStream.resetState`, and matching `CompressionInputStream`.

Control flow: helper instantiates a codec by class name, generates `count` key/value records into `DataOutputBuffer`, writes them through a compression stream, calls `finish`, `flush`, and `resetState`, regenerates the same bytes from the same seed, resets the compressed buffer, creates a new output stream, writes/compresses again, then decompresses and compares every decoded key/value pair with the regenerated original data.

State and persistence behavior: all buffers are in memory. The method creates a new output stream after reset rather than reusing the same Java object for the second write, but the test still targets codec reset behavior and multi-member correctness.

Dependencies and integration points: integrates with `BZip2Codec`, `GzipCodec`, `ZStandardCodec`, `ZlibFactory`, `RandomDatum`, Hadoop data buffers, and Java buffered data streams.

Risks and edge cases: streams are not consistently closed with try-with-resources, so failures could leak in-memory stream state. It does not assert exact compressed framing, only decompressed equality. The spelling "reseting" appears in logs only.

Test signals: confirms compressed output after reset can be decompressed and matches regenerated deterministic Writable records for all targeted codecs and Gzip parameterized configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressionStreamReuse.java -->
