# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/LengthInputStream.java

Purpose: wraps an `InputStream` with a known length, used when returning metadata streams whose byte length must accompany the stream.

Important APIs/types/functions: constructor stores the wrapped stream and length. `getLength()` returns the supplied length. `getWrappedStream()` exposes the underlying stream reference from `FilterInputStream`.

Control flow: callers receive this from dataset metadata APIs, read through the wrapper as a normal `FilterInputStream`, and use `getLength()` for framing or protocol responses.

State and persistence: stores only an in-memory `long length` and the inherited wrapped stream field. It does not validate that bytes read match the advertised length and does not persist anything.

Dependencies and integration points: used by `FsDatasetSpi.getMetaDataInputStream(ExtendedBlock)` and DataNode block-transfer code that sends block metadata to clients or peers.

Risks: length correctness depends entirely on the creator. Exposing `getWrappedStream()` allows callers to bypass wrapper identity, though behavior is still the same stream. No special close behavior beyond `FilterInputStream`.

Test signals: verify length is preserved, wrapper delegates read/close behavior, and metadata APIs populate length from actual meta file size.
