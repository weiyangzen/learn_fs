# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestWeakReferenceMap.java

Purpose: Tests `WeakReferenceMap` and `WeakReferenceThreadMap` basic behavior without trying to force garbage collection. It validates explicit puts/removes, pruning of null weak-reference values, demand creation, lost-reference callbacks, and thread-id keyed convenience methods.

Important APIs/types/functions: `setup()` builds a `WeakReferenceMap<Integer, String>` from `factory()` and `referenceLost()`. Test methods cover `testBasicOperationsWithValidReferences()`, `testPruneNullEntries()`, `testDemandCreateEntries()`, `testFactoryReturningNull()`, and `testWeakReferenceThreadMapAssignment()`. Assertion helpers wrap `get()`, `containsKey()`, `size()`, `prune()`, and callback count checks.

Control flow: The tests insert entries, overwrite key `1`, remove and clear entries, then simulate collected weak references by explicitly storing `null`. A `get()` of absent or null-valued entries invokes the factory and optionally records a lost-reference callback. The thread-map test binds values to the current thread, verifies repeated set/remove behavior, forbids explicit null set, then simulates collection by putting null at the current thread id and requiring recreation.

State and persistence behavior: Each test gets a fresh map and lost-reference list via `@BeforeEach`. `WeakReferenceThreadMap` keeps values keyed by thread id and tracks factory/lost counters through `AtomicLong`. No GC-dependent timing is used, making the tests deterministic but limited to explicit null simulation.

Dependencies and integration points: Depends on Hadoop `WeakReferenceMap`, `WeakReferenceThreadMap`, `LambdaTestUtils.intercept`, AssertJ, and JUnit. These utilities support per-key or per-thread cached resources that should be recreated after weak references clear.

Risks: Not forcing GC means real weak-reference clearing races, reference-queue behavior, and concurrent access are not covered. The callback count contract is important: replacing a null reference via `get()` increments lost count, while normal demand creation does not.

Test signals: Map size/contains assertions, callback list size, null-factory `NullPointerException`, current-thread set/remove return values, and recreation counters are the meaningful regression signals.
