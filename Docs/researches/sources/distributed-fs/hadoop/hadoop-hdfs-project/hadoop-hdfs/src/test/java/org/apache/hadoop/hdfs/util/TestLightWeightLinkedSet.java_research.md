# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestLightWeightLinkedSet.java

Purpose: validates `LightWeightLinkedSet`, a compact set that preserves insertion/poll order and maintains a bookmark iterator.

Important APIs/types/functions: `add`, `addAll`, `remove`, `contains`, `iterator`, `pollFirst`, `pollAll`, `pollN`, `clear`, `toArray`, `getBookmark`, `resetBookmark`.

Control flow: setup mirrors the hash-set test with 100 random integers. Basic tests assert empty/single/multiple collection behavior and insertion-order iteration. Removal tests check removed membership and remaining order. Poll tests verify FIFO-like `pollFirst`, `pollN`, and order after re-adding previously polled elements. Clear resets size, polling, iterators, and bookmark behavior. Bookmark-specific tests verify that `getBookmark` resumes from the advanced position, advances when the bookmarked element is removed, initializes on add to empty, and resets to head.

State and persistence behavior: in-memory collection state only. Random input varies per run; order expectations use the generated list's order.

Dependencies and integration points: collection utility used by HDFS for ordered lightweight tracking; tests rely on JUnit timeouts for bookmark edge cases.

Risks: same low-probability duplicate risk as the hash-set test because random integers are expected to be unique in `add` assertions. Bookmark tests encode internal cursor semantics, so refactors must preserve that public behavior.

Test signals: ordered iteration/polling, removal consistency, empty behavior, array conversion, bookmark movement, and bookmark reset.
