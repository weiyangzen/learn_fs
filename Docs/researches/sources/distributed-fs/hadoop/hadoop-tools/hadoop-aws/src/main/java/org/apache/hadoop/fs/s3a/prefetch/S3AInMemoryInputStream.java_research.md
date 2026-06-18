<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3AInMemoryInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3AInMemoryInputStream.java

Purpose: optimized prefetch stream for small objects whose length is less than or equal to the configured prefetch block size. It loads the full object into one `ByteBuffer`.

Important APIs/types/functions: constructor allocates `ByteBuffer` sized to the object length. `ensureCurrentBuffer()` lazily reads the full file through `S3ARemoteObjectReader` the first time data is needed, wraps it in `BufferData`, and later only updates `FilePosition` for seeks.

Control flow: first read fills the entire buffer from offset zero; subsequent reads and seeks reuse the same in-memory buffer until close.

State/persistence: object contents are held in heap memory for the stream lifetime. No disk persistence.

Dependencies/integration: extends `S3ARemoteInputStream` and uses prefetch framework `BufferData`/`FilePosition`.

Risks/test signals: object length is cast to int after the wrapper's block-size decision; large unexpected lengths would be unsafe. Tests should cover empty file behavior, first-read load, lazy seek, EOF, and close path inherited from the superclass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/prefetch/S3AInMemoryInputStream.java -->
