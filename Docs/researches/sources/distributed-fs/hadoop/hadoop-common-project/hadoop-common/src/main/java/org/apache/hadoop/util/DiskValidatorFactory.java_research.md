# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DiskValidatorFactory.java

Purpose: `DiskValidatorFactory` returns singleton validator instances by class or configured validator name.

Important APIs and types: static concurrent `INSTANCES` cache, `getInstance(Class<? extends DiskValidator>)`, and `getInstance(String)`. Recognized names include `BasicDiskValidator.NAME` and `ReadWriteDiskValidator.NAME`; other strings are loaded as class names.

Control flow: class lookup first checks the cache, otherwise creates an instance with `ReflectionUtils.newInstance`, inserts with `putIfAbsent`, and returns the existing racing instance if any. String lookup maps known aliases or loads a class with `Class.forName`, wrapping class-not-found in `DiskErrorException`.

State and persistence behavior: process-global singleton cache keyed by validator class. No persistence.

Dependencies and integration points: used by configuration-driven disk checking; depends on `ReflectionUtils`, `BasicDiskValidator`, `ReadWriteDiskValidator`, and `DiskChecker.DiskErrorException`.

Risks: custom class strings are unchecked until cast/instantiation, so non-validator classes can fail at runtime. `containsKey` plus `get` is harmless but non-atomic and followed by `putIfAbsent`. Singleton validators must be stateless or thread-safe.

Test signals: cover alias lookup, custom class lookup, class-not-found wrapping, singleton reuse, concurrent get races, non-validator class failure, and cache visibility for tests.
