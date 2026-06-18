# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsUrlConnection.java

Purpose: `FsUrlConnection` adapts Java `URLConnection` to Hadoop `FileSystem` reads so registered URL protocols can return Hadoop-backed input streams.

Important APIs: constructor, `connect`, and `getInputStream`.

Control flow and state: it stores `Configuration` and a single `InputStream`. `connect` rejects double connects, converts the `URL` to a `URI`, resolves the `FileSystem`, and opens a `Path`. Opaque relative `file:` URIs use the scheme-specific part because `URI#getPath` is null for those forms. `getInputStream` lazily connects.

Dependencies and integration: created by `FsUrlStreamHandler`, uses `FileSystem.get(uri, conf)`, `Path`, and precondition checks.

Risks: the connection owns an input stream but does not override close; callers must close the returned stream. Double `connect` is illegal. URI syntax errors become `IOException`.

Test signals: normal HDFS/file URL open, opaque relative file URL handling, lazy connection, double-connect failure, null argument preconditions, and unknown filesystem scheme behavior via the factory.
