# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/dynamic/TestDynConstructors.java

Purpose: Unit tests for reflective constructor discovery and invocation in `DynConstructors`. The tests verify missing implementation behavior, first matching implementation selection, string class-name lookup, hidden constructor access, argument validation, and checked exception wrapping.

Important APIs/types/functions: Tests use `DynConstructors.Builder`, `impl()`, `hiddenImpl()`, `buildChecked()`, `build()`, and `DynConstructors.Ctor.newInstanceChecked()/newInstance()`. They use `Concatenator` as the target and `LambdaTestUtils.intercept()` for expected exceptions.

Control flow: Missing-builder, missing-class, and missing-constructor tests assert `NoSuchMethodException` from checked builds and runtime failures from unchecked builds. First-match tests add a fake class before valid constructors and assert the first valid constructor wins. Exception tests build the `Exception` constructor and require checked invocation to rethrow the original checked exception while unchecked invocation wraps it. Hidden-constructor tests demonstrate that normal method lookup cannot find private members, but `hiddenImpl()` can find the private char constructor.

State and persistence behavior: No persistent state beyond constructed `Concatenator` instances and their separators. Builder state is ordered; implementation registration order is part of the contract.

Dependencies and integration points: Depends on Hadoop dynamic reflection helpers, JUnit, and Hadoop test interception helpers. These utilities support optional dependency/version compatibility where code attempts multiple reflective constructors.

Risks: Tests are sensitive to reflection access restrictions in newer Java runtimes and module boundaries. The unchecked build path intentionally wraps failures in runtime exceptions, so exact wrapper type/message coverage is limited. Builder order changes would alter first-implementation behavior.

Test signals: Expected `NoSuchMethodException`, `RuntimeException`, `IllegalArgumentException`, original checked exception propagation, non-null hidden constructor, and correct separator output demonstrate the constructor helper contract.
