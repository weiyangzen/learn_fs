# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/WritableName.java

## Purpose

`WritableName.java` maps writable classes to stable short names and alternate names so serialized files can survive Java class renames or use compact legacy aliases.

## Important APIs, types, and functions

- Static maps `NAME_TO_CLASS` and `CLASS_TO_NAME` hold aliases.
- Static initialization registers `NullWritable` as `null`, `LongWritable` as `long`, `UTF8` as `UTF8`, and `MD5Hash` as `MD5Hash`.
- `setName(Class<?>, String)` sets the canonical short name and reverse mapping.
- `addName(Class<?>, String)` adds an alternate lookup-only name.
- `getName(Class<?>)` returns a registered name or the Java class name.
- `getClass(String, Configuration)` resolves an alias or falls back to `conf.getClassByName()`, wrapping `ClassNotFoundException` in `IOException`.

## Control flow

Class-to-name lookup is a synchronized map read with fallback to `Class.getName()`. Name-to-class lookup is a synchronized alias read with fallback class loading via the supplied `Configuration`. `setName()` updates both maps, while `addName()` only updates name-to-class.

## State and persistence behavior

The alias maps are static mutable JVM-global state. Persisted data elsewhere, especially old sequence files and object-writable formats, may contain either aliases or full class names. Alias registration changes future serialization and lookup behavior but does not rewrite existing data.

## Dependencies and integration points

The class depends on `Configuration` for class loading and several writable types for default aliases. `SequenceFile.Reader` uses it to resolve key/value class names read from headers.

## Risks and edge cases

- Global synchronized maps can be changed by any code in the JVM, affecting all readers/writers.
- `setName()` can overwrite aliases without conflict checks.
- `getClass()` assumes `conf` is non-null; callers passing null risk `NullPointerException`.
- Alias collisions can make historical data resolve to the wrong class.

## Test signals

Tests should cover default aliases, custom aliases, alternate names, fallback class loading, missing class error wrapping, alias overwrite behavior, and sequence-file compatibility with renamed classes.
