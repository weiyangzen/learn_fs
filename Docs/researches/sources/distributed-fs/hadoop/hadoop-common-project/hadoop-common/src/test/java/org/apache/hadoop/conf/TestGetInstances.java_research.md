# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestGetInstances.java

## Purpose

`TestGetInstances` verifies `Configuration.getInstances`, which instantiates a comma-separated list of class names from a configuration property and enforces assignability to a requested interface type.

## Important APIs and types

- `Configuration.getInstances(String propertyName, Class<T> xface)`.
- `Configuration.setStrings` for class-name lists.
- Local marker interfaces `SampleInterface` and `ChildInterface`.
- Local implementation classes `SampleClass` and `AnotherClass` with package-private zero-argument constructors.

## Control flow

The test first reads a missing property and an empty property and expects empty lists. It then writes two valid implementation class names and expects two `SampleInterface` instances. Finally, it writes a list containing `String.class` and expects a runtime failure because `String` does not implement the requested interface, then writes a nonexistent class name and expects another runtime failure.

## State and persistence behavior

All state is in a local `Configuration`. The instantiated objects are not persisted and have no behavior beyond type compatibility.

## Dependencies and integration points

The file covers the reflection path inside `Configuration`, class-name parsing from configuration values, constructor access, and runtime type checks. This utility is used by Hadoop plugin-style extension points.

## Risks and edge cases

- The test only catches broad `RuntimeException`, so it does not pin exact exception type or message.
- It does not validate object order or concrete class types beyond list size for valid classes.
- Constructor visibility is package-private; behavior may differ for public classes, non-zero-arg constructors, abstract classes, or classes loaded by a custom class loader.

## Test signals

The core signals are empty-list behavior for missing/empty config, successful instantiation of assignable classes, and failure for non-assignable or missing classes.
