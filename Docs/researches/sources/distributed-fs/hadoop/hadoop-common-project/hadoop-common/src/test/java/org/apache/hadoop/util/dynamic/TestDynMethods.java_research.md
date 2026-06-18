# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/dynamic/TestDynMethods.java

Purpose: Comprehensive tests for `DynMethods` reflective method discovery and invocation. It covers ordered implementation selection, overload/varargs invocation, hidden methods, bound methods, static methods, constructor adapters, no-op fallback, incorrect arguments, and checked exception propagation.

Important APIs/types/functions: Tests use `DynMethods.Builder`, `impl()`, `hiddenImpl()`, `ctorImpl()`, `orNoop()`, `buildChecked()`, `build()`, `buildStaticChecked()`, `buildStatic()`, `UnboundMethod.invoke()/invokeChecked()/bind()/isStatic()/isNoop()/asStatic()`, `BoundMethod`, and `StaticMethod`. `Concatenator` is the reflection target.

Control flow: The test suite first verifies failure paths for no implementations, missing classes, and missing methods. First-match tests register fake and real overloads, proving earlier valid implementations win, extra arguments are ignored, and missing arguments are null-padded. Other tests invoke varargs through an `Object` array, verify wrong argument types raise `IllegalArgumentException`, rethrow checked exceptions through checked invocation, remap method names, look up methods by string class name, access private `setSeparator()` through `hiddenImpl()`, bind methods to different target instances, and enforce static/non-static constraints.

State and persistence behavior: State exists only in target `Concatenator` separators and builder method lists. No-op methods are stateless and can be unbound, bound to null or an object, or treated as static while always returning null. Constructor adapter state creates new `Concatenator` instances through `ctorImpl()`.

Dependencies and integration points: Depends on Hadoop dynamic reflection helpers, the `Concatenator` fixture, JUnit, and Hadoop `LambdaTestUtils`. Dynamic methods are used for optional APIs and cross-version compatibility where Hadoop must reflectively call methods when present.

Risks: Reflection behavior may vary with Java access controls, especially private hidden methods. The helper's argument trimming/null padding is powerful but risky because wrong arity may not fail in some cases. Static binding constraints protect misuse but require accurate method modifier detection.

Test signals: Correct concatenated strings, private separator update, expected exceptions for bad discovery/invocation/binding, static status checks, constructor adapter behavior, and no-op null returns are the primary signals.
