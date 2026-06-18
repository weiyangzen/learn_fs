## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/AvroFSInput.java

Purpose: adapts Hadoop `FSDataInputStream` to Avro's `SeekableInput` interface so Avro readers can consume Hadoop filesystem files with seek and position support.

Important APIs and types: constructors accept either an existing `FSDataInputStream` plus length or a `FileContext` and `Path`; implements Avro `SeekableInput` methods `length`, `read`, `seek`, `tell`, and `Closeable.close`.

Control flow: the `FileContext` constructor fetches `FileStatus` to capture length, builds an async open request with sequential read policy and the known status, waits for the future through `FutureIO.awaitFuture`, then delegates all I/O calls to the opened stream.

State and persistence behavior: stores only the wrapped stream and immutable length. No persistence is performed beyond reads against the underlying filesystem.

Dependencies and integration points: bridges Hadoop `FileContext`, `Path`, `FileStatus`, `FSDataInputStream`, `Options.OpenFileOptions`, and Apache Avro `SeekableInput`.

Risks: caller-supplied length can be stale or wrong in the direct constructor. The `FileContext` constructor blocks awaiting an async builder result and can surface open failures before Avro begins reading. It assumes sequential policy is suitable for Avro access, though Avro can seek.

Test signals: verify length from status, read delegation, seek/tell consistency, close propagation, and open-builder options when constructed from `FileContext`.
