# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/dynamic/Concatenator.java

Purpose: Test fixture class for `DynMethods` and `DynConstructors`. It supplies overloaded constructors, overloaded instance methods, a private constructor, a private setter, checked-exception throwing paths, varargs methods, and a static factory-like method.

Important APIs/types/functions: Public constructors include no-arg, `Concatenator(String sep)`, and `Concatenator(Exception e) throws Exception`; a private `Concatenator(char sep)` tests hidden constructor access. `SomeCheckedException` is a checked marker. Methods include private `setSeparator(String)`, overloads `concat(String,String)`, `concat(String,String,String)`, `concat(Exception)`, varargs `concat(String...)`, static `cat(String...)`, and static `newConcatenator(String)`.

Control flow: Constructors set the separator or throw the supplied exception. `concat` overloads join arguments using `sep`; the varargs version returns null for zero arguments and otherwise loops through the array. The exception overload rethrows the supplied exception to test reflective checked exception propagation.

State and persistence behavior: The only state is instance field `sep`, initialized to empty string and mutated by constructors or private `setSeparator()`. No external persistence exists. Hidden-access tests rely on reflective accessibility rather than public API.

Dependencies and integration points: Depends only on Java language/runtime features and is consumed by `TestDynMethods` and `TestDynConstructors`. It is derived from Parquet utility tests, serving as a stable reflection target for Hadoop dynamic invocation helpers.

Risks: Because this fixture intentionally exposes private members for tests, changing visibility or signatures can break dynamic helper coverage. Overload resolution tests depend on argument count and type erasure/varargs behavior matching the fixture exactly.

Test signals: Expected concatenated strings with different separators, private separator mutation, static varargs invocation, constructor selection, and checked exception propagation are all derived from this fixture.
