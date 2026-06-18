# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/AssertExtensions.java

Purpose: small AssertJ helper for lazy failure descriptions.

Important APIs/types/functions: final `AssertExtensions`, static `dynamicDescription(Callable<String>)`, nested `DynamicDescription extends Description`, and logger-backed error handling.

Control flow: `dynamicDescription` wraps a callable. AssertJ invokes `Description.value()` only when needed; the wrapper calls the callable and returns its result. If evaluation fails, it logs a warning/debug detail and returns null so AssertJ can skip the description.

State and persistence behavior: stores a callable reference in memory. No persistent state.

Dependencies and integration points: deliberately isolated from `LambdaTestUtils` so AssertJ is only required where this class is used. Integrates with AssertJ `describedAs`.

Risks and test signals: protects expensive diagnostic rendering from running on passing assertions and prevents diagnostic failures from hiding the original assertion. Risk is silent null descriptions if the callable fails.
