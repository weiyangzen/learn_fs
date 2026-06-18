# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestStringInterner.java

Purpose: tests strong and weak string interning helpers in `StringInterner`.

Important APIs and types: `StringInterner.strongIntern`, `StringInterner.weakIntern`, Java string literals, substrings, and heap-created strings.

Control flow: `testNoIntern` proves three equal strings are distinct references before interning. `testStrongIntern` interns literal, substring, and heap string and expects all returned references to be the same. `testWeakIntern` repeats the same identity assertion for the weak interner.

State and persistence: strong and weak interners keep process-local caches; weak cache entries may be GC-sensitive, but this test holds strong references during assertions.

Dependencies and integration points: interning reduces memory use and enables identity sharing for common Hadoop strings.

Risks: returning distinct instances breaks memory-sharing assumptions; weak interner implementation must still canonicalize while entries are live. Test signals are `assertNotSame` before interning and `assertSame` after each interning mode.
