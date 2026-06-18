# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/statistics/impl/TestEvaluatingStatisticsMap.java

Purpose: Tests `EvaluatingStatisticsMap`, a map-like structure whose values are provided by functions evaluated on access/iteration.

Important APIs/types/functions: `EvaluatingStatisticsMap<String>`, `addFunction`, `keySet`, `values`, `entrySet`, `get`, and `forEach`.

Control flow: The test starts with an empty map and asserts all views are empty. It then loads one function per environment variable, where each function returns that variable's value. It asserts key sets match `System.getenv().keySet()`, values match environment values, direct `get(k)` returns each expected value, and `forEach` emits entries matching the environment map.

State/persistence: Reads process environment variables but does not mutate them. The map stores function closures.

Dependencies/integration: Verifies the lazy/evaluating map abstraction used by dynamic IO statistics maps.

Risks: Environment variable values can contain duplicates, but `containsExactlyInAnyOrderElementsOf` handles multiset-like collection comparison. The test depends on a stable environment during the test run.

Test signals: Empty initial views, complete key/value coverage, direct lookup correctness, and `forEach` evaluation correctness.
