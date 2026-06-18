# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigurationDeprecation.java

## Purpose

`TestConfigurationDeprecation` focuses on `Configuration` key deprecation and aliasing. It verifies old-key/new-key consistency, multi-target deprecations, final-parameter interaction, iterator and unset behavior, warning behavior, concurrent deprecation mutation, late deprecation registration after resource loading, and the absence of deprecated properties in `core-default.xml`.

## Important APIs and types

- `Configuration.addDeprecation`, `addDeprecations`, `DeprecationDelta`, `isDeprecated`, and `hasWarnedDeprecation`.
- Aliased property access through `get`, `set`, `unset`, `iterator`, and `writeXml`.
- Final-parameter behavior through XML `<final>true</final>` and empty final values.
- Threading support through `ScheduledThreadPoolExecutor`, `CountDownLatch`, `Future`, `ThreadFactoryBuilder`, and Guava `Uninterruptibles`.
- DOM parsing of `/core-default.xml` to bypass `Configuration` normalization for the no-default-deprecations assertion.

## Control flow

`addDeprecationToConfiguration` registers simple and multi-new-key mappings. `testDeprecation` loads old and new keys from XML resources, verifies aliases agree, then changes values through old and new names. `testDeprecationForFinalParameters` loads final old/new keys, overlays later resources, and checks which values are protected by final status.

Smaller tests cover setting old keys before deprecation registration, default-resource old-key migration, iterator visibility of both deprecated and replacement keys, and `unset` propagation across aliases. `testConcurrentDeprecateAndManipulate` starts deprecation-registration tasks and configuration access tasks together and expects no race failures. Warning tests distinguish use of deprecated keys from use of replacement keys. `testGetPropertyBeforeDeprecetionsAreSet` loads an old YARN ZooKeeper key before adding its deprecation mapping, then verifies both aliases work. `testNoDeprecationsByDefault` parses the default XML directly and fails if any property is already registered as deprecated.

## State and persistence behavior

The test writes four temporary XML files and deletes them in teardown. Deprecation mappings are global static state in `Configuration`, so unique test key names are important. A static initializer adds `test-fake-default.xml` as a default resource, affecting default-loading behavior for tests that use `new Configuration()`.

## Dependencies and integration points

The file ties deprecation behavior to `CommonConfigurationKeys`, `Path` resource loading, XML serialization, default resources, `core-default.xml`, and multi-threaded access. It is a compatibility guard for renamed configuration keys across Hadoop releases.

## Risks and edge cases

- Static deprecation mappings can leak across tests and processes; repeated names can hide defects.
- Multi-new-key mappings resolve to the most recent value among aliases; this is subtle and can surprise callers.
- Final parameters can be set through either old or new names, so both alias directions must share final state.
- Warning-state checks depend on global `hasWarnedDeprecation` tracking.
- Concurrent deprecation registration and configuration access can reveal synchronization bugs but the test is probabilistic.

## Test signals

The strongest signals are alias consistency across XML loading, programmatic set/unset, iteration, final protection, and concurrent registration/access. Additional useful tests would isolate global deprecation cleanup and cover serialization of multi-new-key mappings with final parameters.
