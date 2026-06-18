# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/MoreAsserts.java

Purpose: small assertion helper class for collection equality, CompletableFuture completion state, and AssertJ equality messages.

Important APIs/types/functions: overloaded `assertEquals` for arrays/iterables and iterable/iterable, `assertFutureCompletedSuccessfully`, `assertFutureFailedExceptionally`, and `assertEqual`.

Control flow: iterable assertions compare element-by-element and then assert neither side has extra elements. Future assertions inspect `isDone` and `isCompletedExceptionally`. `assertEqual` delegates to AssertJ with a formatted description.

State and persistence behavior: no state; pure assertion utilities.

Dependencies and integration points: combines JUnit assertions and AssertJ. Intended as supplementary helpers where standard assertions are verbose.

Risks and test signals: collection assertions report index-specific mismatches but use terse extra-element messages. Future assertions check state only; they do not retrieve results or inspect failure causes.
