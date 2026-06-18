# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestIdentityHashStore.java

Purpose: verifies `IdentityHashStore`, a small identity-keyed multimap-like store that uses object identity rather than `equals()` or `hashCode()` for keys.

Important APIs and types: `IdentityHashStore<K,V>`, `put`, `get`, `remove`, `visitAll`, `isEmpty`, `numElements`, `capacity`, and `IdentityHashStore.Visitor`. The nested `Key` deliberately throws from `hashCode()` and implements value equality to prove that neither Java hash nor equality is used.

Control flow: tests start with zero and nonzero initial capacity, visit empty stores, insert values, look them up by the same object, attempt lookup with a value-equal but distinct key, insert duplicate entries for the same identity key, remove each duplicate, and bulk insert/remove 1000 unique keys.

State and persistence: all state is in-memory open-addressed identity storage. Capacity grows from zero on demand; after 1000 additions/removals the test expects capacity 1024, so resizing behavior is part of the contract.

Dependencies and integration points: depends only on Hadoop's store class, JUnit assertions, timeouts, and SLF4J debug logging.

Risks: replacing identity comparison with `equals`, collapsing duplicate identity-key inserts, invoking user `hashCode`, or mishandling tombstones/resize would break core assumptions. Test signals include `assertNull` for equal-but-distinct key lookup, visitor checks, empty-state checks, and final capacity assertion.
