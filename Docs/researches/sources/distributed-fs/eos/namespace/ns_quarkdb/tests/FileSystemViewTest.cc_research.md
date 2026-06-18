# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/FileSystemViewTest.cc

Purpose: Integration and unit tests for filesystem accounting views, QDB set handlers, iterators, random file selection, and change-list behavior.
Important APIs/types/functions: helpers `getRandomLocation`, `countReplicas`, `countUnlinked`; tests cover `RequestBuilder` fs keys, `parseFsId`, `FileSystemView`, `StreamingFileListIterator`, `FileSystemHandler`, cache clearing, and `SetChangeList`.
Control flow: `BasicSanity` creates thousands of files under a hierarchy, assigns/removes/unlinks locations, flushes, restarts, validates replica/unlinked/no-replica counts, URI lookup, and cleanup. Other tests populate QDB sets, verify list/streaming iterators, mutate handlers, clear caches after clock advances, and apply pending set changes.
State/persistence: heavily exercises QDB sets under `fsview:*`, flusher durability, and in-memory cache status.
Dependencies/integration: depends on qclient `QSet`, Folly executor, filesystem accounting classes, hierarchical view, and test utilities.
Risks: random data and large counts can be slow/flaky with an underprovisioned QDB; cache tests use a test harness private-clock hook.
Test signals: broad coverage of filesystem view persistence, iterator completeness, handler backend consistency, cache eviction timing, and set delta semantics.
