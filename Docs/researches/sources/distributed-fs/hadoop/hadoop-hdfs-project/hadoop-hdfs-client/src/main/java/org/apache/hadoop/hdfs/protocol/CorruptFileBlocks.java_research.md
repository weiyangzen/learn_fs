# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/CorruptFileBlocks.java

## Purpose
`CorruptFileBlocks` is a small immutable response object for `ClientProtocol.listCorruptFileBlocks`. It carries a batch of corrupt file paths plus a cookie used as the cursor for subsequent calls.

## APIs and Behavior
The default constructor returns an empty file array and empty cookie. The primary constructor stores `String[] files` and `String cookie`, exposed through `getFiles()` and `getCookie()`. Equality requires both cookie equality and array-content equality via `Arrays.equals`; `hashCode()` folds each file into the cookie hash using a fixed prime.

## State, Dependencies, and Integration
There is no persistence or control flow beyond value comparison. The class depends only on `java.util.Arrays` and is serialized through the HDFS client protocol conversion layer. It is consumed by admin and fsck-like clients that repeatedly call NameNode corrupt-file listing until the returned cookie/list indicates exhaustion.

## Risks and Test Signals
The constructor does not defensively copy `files`, so callers retaining the original array can mutate an instance after construction. Tests should cover empty responses, repeated-cookie pagination, equality/hash consistency, and mutation hazards if the object is stored in maps or caches.
