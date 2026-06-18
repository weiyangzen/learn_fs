# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/StorageAdapter.java

Purpose: this small test adapter exposes package-private `Storage` internals to tests that need to replace a `StorageDirectory` with a Mockito spy.

Important APIs and types: `Storage`, `Storage.StorageDirectory`, and Mockito. The only public API is `spyOnStorageDirectory(Storage s, int idx)`.

Control flow: `spyOnStorageDirectory` retrieves the storage directory at the requested index, wraps it with `Mockito.spy`, replaces the element in `Storage.getStorageDirs()`, and returns the spy to the caller. There are no assertions or test methods here; it is a helper used by other test classes.

State and persistence: the helper mutates the in-memory list of storage directories inside a `Storage` instance. It does not touch disk directly, but callers generally use it to observe or alter behavior around filesystem-backed storage directories.

Dependencies and integration points: this file is in the same package as `Storage`, so it can access package-private state that downstream tests cannot reach directly. It is a bridge between HDFS storage internals and Mockito-based verification.

Risks: replacing a real storage directory with a spy can subtly affect identity comparisons, final method behavior, or serialization assumptions. Because it mutates shared storage state in place, callers must avoid leaking the spied object across unrelated tests.

Test signals: there are no local test signals. Its correctness is reflected by tests that can verify interactions on `StorageDirectory` without reimplementing storage internals.
