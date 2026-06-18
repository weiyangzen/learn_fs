# Research: subset-b-008024 Apache Ozone HDDS framework web, configuration, filesystem, SCM, and security tests

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/resources/webapps/static/ozone.js -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/resources/webapps/static/ozone.js

## Purpose

This file defines the AngularJS front-end module for the legacy HDDS/Ozone web UI. It wires routes for the main page, RPC metrics page, and configuration page, and provides components for overview JMX data, JVM parameters, RPC metric visualization, tabs, navigation, and configuration filtering.

## Important APIs, Types, And Functions

The main Angular module is `ozone`, with dependencies on `nvd3` and `ngRoute`. Components include `overview`, `jvmParameters`, `rpcMetrics`, `rpcMetric`, `tabs`, `pane`, `navmenu`, and `config`. `isIgnoredJmxKeys()` filters JMX metadata keys from metrics output. The `rpcMetric` controller builds grouped structures for latency percentiles, success/failure counters, operation counts, averages, and unmatched metrics. The `config` controller calls `conf?cmd=getOzoneTags` and `conf?cmd=getPropertyByTag`.

## Control Flow

The route provider maps `/`, `/metrics/rpc`, and `/config` to either static templates or component tags. Components load server-side JSON via `$http` after instantiation. RPC metrics are collected from the Hadoop JMX endpoint and reshaped whenever `jmxdata` changes. Configuration first loads tags, removes legacy excluded tags, loads all tagged configuration entries, normalizes them into an array, and applies component/tag filters and sorting.

## State And Persistence

State is entirely browser-side controller state: selected tabs, selected config tags, normalized config arrays, JMX data, and a docs-link availability flag. There is no local persistence. The source depends on server endpoints for durable configuration and metrics.

## Dependencies And Integration Points

The UI integrates with Hadoop JMX endpoints, the HDDS configuration servlet, `static/templates/*.html`, AngularJS, ngRoute, nvd3, d3 formatting, and optional `docs/index.html`.

## Risks

The file uses older AngularJS idioms and loose equality. `Object.values` can be a browser compatibility risk in very old environments. Configuration filtering mutates `ctrl.configs` from the normalized master map, so missed calls to `reloadConfig()` can compound filters. JMX metric grouping depends on name regexes, so renamed metrics silently fall into `others`.

## Test Signals

Useful signals include loading all routes, successful JMX and `conf` requests, visual RPC percentile charts, config sorting and filtering by component/tag, docs-link presence/absence behavior, and browser console checks for missing templates or unsupported JavaScript APIs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/resources/webapps/static/ozone.js -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/conf/TestHddsConfServlet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/conf/TestHddsConfServlet.java

## Purpose

This JUnit class verifies `HddsConfServlet` and shared servlet response helpers for configuration dump, single-property lookup, tag discovery, tag-based lookup, JSON serialization, XML serialization, and error handling.

## Important APIs, Types, And Functions

Important helpers are `getResultWithCmd()`, `verifyGetProperty()`, `getTestConf()`, and `getPropertiesConf()`. The nested `OzoneTestConfig` class supplies annotated config metadata through `@ConfigGroup` and `@Config`. The tests exercise `HddsConfServlet.doGet`, `HttpServletUtils.writeResponse`, `OzoneConfiguration.dumpConfiguration`, `OzoneConfiguration.TAGS`, `OzoneConfiguration.getObject`, and `OzoneConfiguration.writeXml`.

## Control Flow

Each servlet test constructs an `OzoneConfiguration`, mocks `ServletConfig`, `ServletContext`, request, and response, injects the configuration through `HttpServer2.CONF_CONTEXT_ATTRIBUTE`, invokes `doGet`, and inspects the captured writer output. Property lookup iterates across XML and JSON accept headers and across found, missing, empty, and null names. Command tests dispatch through `cmd=getOzoneTags`, `cmd=getPropertyByTag`, and an illegal command.

## State And Persistence

State is in-memory only: static test maps, mock request parameters, a per-test `OzoneConfiguration`, and `StringWriter` output. The nested annotated config object is registered into the configuration metadata cache by `conf.getObject(OzoneTestConfig.class)`.

## Dependencies And Integration Points

The tests integrate servlet APIs, Mockito, AssertJ, Jackson JSON parsing, secure XML parsing via `XMLUtils`, and HDDS HTTP response utilities. They protect the UI endpoint consumed by `ozone.js`.

## Risks

The test compares exact XML for invalid commands, so harmless formatter changes can break it. `TEST_FORMATS.get(null)` intentionally produces a null accept header in command tests; servlet default-format behavior must remain stable. The tests do not parse the full XML/JSON single-property responses structurally.

## Test Signals

Signals include 404 status for missing properties, inclusion/exclusion of config keys in responses, presence of programmatic resource metadata in JSON, valid XML parse with expected value, tag JSON equality, and illegal-command XML error output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/conf/TestHddsConfServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/conf/TestReconfigurationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/conf/TestReconfigurationHandler.java

## Purpose

This test class validates `ReconfigurationHandler` registration, listing, mutation, validation, unknown-property behavior, and admin-access checks for dynamically reconfigurable settings.

## Important APIs, Types, And Functions

The subject is built from `new ReconfigurationHandler("test", config, op -> adminCheck.get().accept(op))`, then registers two explicit setters and one annotated `SimpleConfiguration` object. Test constants cover explicit properties and generated keys `test.scm.client.compression.enabled` and `test.scm.client.wait`. `CheckedConsumer<String, IOException>` models accept/deny admin checks.

## Control Flow

Initialization registers property handlers before tests run. `getProperties()` and `listProperties()` compare exact sets/lists. `callsReconfigurationFunction()` updates atomic references and object-backed fields through `reconfigureProperty`. `validatesNewConfiguration()` rejects invalid wait time and confirms state preservation. `requiresAdminAccess()` swaps the admin checker to throw and verifies list/start/status calls propagate `IOException`.

## State And Persistence

State is per-test in-memory `OzoneConfiguration`, `AtomicReference` fields, and a mutable config object. No persistent store is used. Failed validation must leave object state unchanged.

## Dependencies And Integration Points

The class exercises HDDS config annotations, Hadoop `ReconfigurationException`, Ratis checked consumers, and the handler methods that are used by HTTP/admin reconfiguration endpoints.

## Risks

The exact expected property set is a compatibility guard; adding new annotated mutable properties requires updating the test intentionally. Unknown property behavior differs between `reconfigurePropertyImpl` and public `reconfigureProperty`, which callers must understand.

## Test Signals

Signals include exact property enumeration, successful setter callbacks, rejected invalid values, no throw for implementation-level unknown property, exception for public unknown property, and enforced admin checks on privileged methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/conf/TestReconfigurationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/conf/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/conf/package-info.java

## Purpose

This package-info file documents that `org.apache.hadoop.hdds.conf` test sources contain configuration-related tests.

## Important APIs, Types, And Functions

It declares the package and has no classes, methods, annotations, or runtime API.

## Control Flow

There is no executable control flow. The Java compiler associates the package Javadoc with the test package.

## State And Persistence

No state or persistence exists.

## Dependencies And Integration Points

The file integrates only with Java package documentation tooling and the surrounding test package.

## Risks

Risk is minimal. The only meaningful maintenance issue is stale package documentation if the test package broadens beyond configuration behavior.

## Test Signals

Compilation of the test package is the only signal needed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/conf/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsageCheckFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsageCheckFactory.java

## Purpose

This final utility class supplies `SpaceUsageCheckFactory` implementations for tests that need deterministic disk-capacity parameters without invoking real disk usage checks.

## Important APIs, Types, And Functions

`NONE` is a reusable no-op factory. `of(SpaceUsageSource, Duration, SpaceUsagePersistence)` creates a lambda factory returning `SpaceUsageCheckParams` for any directory. Nested `None` reports unlimited fixed capacity/available and disables persistence. Nested `HalfTera` reports 512 GiB capacity and available space. The private constructor prevents instantiation.

## Control Flow

Callers request params for a directory through a factory. The factory constructs `SpaceUsageCheckParams` with the supplied or fixed source, refresh period, and persistence strategy.

## State And Persistence

The utility itself is stateless. `None` and `HalfTera` use `SpaceUsagePersistence.None.INSTANCE`, so they deliberately do not persist usage. Factories returned by `of` close over caller-provided dependencies.

## Dependencies And Integration Points

It integrates with `SpaceUsageCheckFactory`, `SpaceUsageCheckParams`, `SpaceUsageSource`, `SpaceUsagePersistence`, and `MockSpaceUsageSource`.

## Risks

Tests using unlimited capacity can mask quota or overflow paths. `HalfTera` reports `used=0` because capacity equals available, so it is not suitable for tests requiring nonzero usage.

## Test Signals

Consumers should verify generated params preserve the target directory, source values, refresh duration, and persistence behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsageCheckFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsageCheckParams.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsageCheckParams.java

## Purpose

This test helper provides a small builder for `SpaceUsageCheckParams`, making space-usage tests concise while defaulting to safe mock values.

## Important APIs, Types, And Functions

`newBuilder(File)` returns a `Builder`. The builder tracks `dir`, `source`, `refresh`, and `persistence`, and exposes `withSource`, `withRefresh`, `withPersistence`, and `build`. Defaults are unlimited usage source, zero refresh interval, and no persistence.

## Control Flow

Tests call `newBuilder(dir)`, override selected fields fluently, and call `build()` to create production `SpaceUsageCheckParams`.

## State And Persistence

Builder state is mutable and short-lived. Default persistence is disabled unless a test injects a `SpaceUsagePersistence`.

## Dependencies And Integration Points

It depends on production `SpaceUsageCheckParams` and test/source helpers `MockSpaceUsageSource` and `SpaceUsagePersistence.None`.

## Risks

The zero-refresh default changes `CachingSpaceUsageSource.start()` behavior compared with periodic production configs. Tests that rely on periodic scheduling must explicitly set a nonzero refresh.

## Test Signals

Signals are indirect through tests that assert constructed params carry expected directory, source, refresh, and persistence values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsageCheckParams.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsagePersistence.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsagePersistence.java

## Purpose

This utility supplies an in-memory `SpaceUsagePersistence` implementation backed by an `AtomicLong`, used to test cached usage loading and saving without files.

## Important APIs, Types, And Functions

`inMemory(AtomicLong)` returns a private `Memory` instance. `Memory.load()` returns `OptionalLong.of(target.get())`; `Memory.save(SpaceUsageSource)` writes `source.getUsedSpace()` into the target.

## Control Flow

Tests pass an `AtomicLong` representing persisted state into `inMemory`, use it in `SpaceUsageCheckParams`, then inspect whether production code loaded or saved the expected value.

## State And Persistence

State lives in the caller-provided `AtomicLong`. It is memory-only persistence, thread-safe at the scalar operation level, and has no expiry or validation logic.

## Dependencies And Integration Points

It implements production `SpaceUsagePersistence` and reads from production `SpaceUsageSource`.

## Risks

Because `load()` always returns a present value, an initial zero represents a present zero, not missing persistence. Tests for missing persisted values must avoid this helper or use production/file persistence semantics.

## Test Signals

Useful signals include assertions that startup reads the atomic value and shutdown/save writes the latest used-space value.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsagePersistence.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsageSource.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsageSource.java

## Purpose

This utility provides deterministic `SpaceUsageSource` instances for tests, including fixed values, unlimited capacity, and dynamic used-space from an `AtomicLong`.

## Important APIs, Types, And Functions

`unlimited()` returns a fixed source with `Long.MAX_VALUE` capacity and available. `fixed(capacity, available)` derives used as `capacity - available`. `fixed(capacity, available, used)` delegates to `SpaceUsageSource.Fixed`. `of(capacity, AtomicLong used)` returns an anonymous source whose used value is dynamic and whose available value is `capacity - used`.

## Control Flow

Tests construct a source and pass it into params, factories, or persistence checks. Production code calls `getUsedSpace`, `getCapacity`, and `getAvailable`.

## State And Persistence

Fixed sources are immutable. Dynamic sources read an external `AtomicLong` and do not persist changes themselves.

## Dependencies And Integration Points

It integrates with `SpaceUsageSource` and its `Fixed` implementation, and is used by multiple space-usage tests.

## Risks

Dynamic available space can become negative if the external used value exceeds capacity. `unlimited()` uses extreme values, so arithmetic in callers must avoid overflow.

## Test Signals

Signals are assertions of exact capacity, available, and used values before and after external atomic updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/MockSpaceUsageSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestCachingSpaceUsageSource.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestCachingSpaceUsageSource.java

## Purpose

This class tests `CachingSpaceUsageSource`, covering initial values, refresh scheduling, persistence on shutdown, bounds handling for used/available updates, snapshot consistency, and thread naming.

## Important APIs, Types, And Functions

The tests use `CachingSpaceUsageSource`, `SpaceUsageCheckParams`, `SpaceUsageSource.snapshot`, `incrementUsedSpace`, `decrementUsedSpace`, `start`, `shutdown`, and `threadFactoryFor`. Helpers include `paramsBuilder`, `sameThreadExecutorWithoutDelay`, `verifyRefreshWasScheduled`, `assertAvailableWasUpdated`, and `assertSnapshotIsUpToDate`.

## Control Flow

Tests construct params with mock sources and persistence. Start behavior either refreshes once immediately when periodic refresh is disabled or schedules two fixed-delay tasks when refresh is configured. Mock executors run scheduled runnables synchronously, making refresh effects deterministic. Shutdown saves current usage, cancels scheduled futures, and shuts down the executor.

## State And Persistence

The subject caches used, capacity, and available values. Persistence is represented by `AtomicLong` through `MockSpaceUsagePersistence`. Boundary tests ensure usage never drops below zero and available never drops below zero while snapshots mirror current state.

## Dependencies And Integration Points

Dependencies include JUnit temp dirs, Mockito scheduled executor/futures, AssertJ, Commons `RandomUtils`, and the mock FS helpers in this package.

## Risks

The synchronous mock executor does not reveal concurrency races in scheduled refresh. Random initial values avoid constants but can complicate reproduction if an edge case depends on exact values. Two futures are expected on shutdown, tying the test to the implementation's dual refresh tasks.

## Test Signals

Signals include correct initial cached value, immediate or delayed schedule parameters, no early persistence before shutdown, saved shutdown value, clamped increments/decrements, ignored negative changes, fresh snapshots, and newline-free thread names ending with sequence numbers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestCachingSpaceUsageSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDU.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDU.java

## Purpose

This class tests the `DU` disk-usage source against real temporary files on non-Windows platforms, including exclude-pattern behavior.

## Important APIs, Types, And Functions

`createFile(File, int)` writes random data via `RandomAccessFile` and syncs it to disk. `testGetUsed()` constructs `new DU(file)`. `testExcludePattern()` constructs `new DU(dir, "*.tmp")`. `assertFileSize()` accepts filesystem slack of 8 KiB.

## Control Flow

`setUp()` skips tests on Windows. Test files are created with random bytes to avoid compression. The subject queries disk usage and assertions compare observed usage with expected written sizes.

## State And Persistence

State is real temporary filesystem state under JUnit `@TempDir`. Files are created and flushed, then removed by the test framework.

## Dependencies And Integration Points

The test integrates with Hadoop `Shell.WINDOWS`, Ozone `KB`, Commons `RandomUtils`, Java file IO, and the production `DU` implementation.

## Risks

Disk usage depends on filesystem block size, metadata overhead, compression, sparse-file behavior, and platform availability of `du`; the slack allowance mitigates but does not eliminate environment sensitivity.

## Test Signals

Signals are used-space values at least the expected written size and no more than expected plus 8 KiB, and exclusion of matching `*.tmp` files from directory totals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDU.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDUFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDUFactory.java

## Purpose

This class validates that `DUFactory` can be selected through configuration and creates expected `SpaceUsageCheckParams`.

## Important APIs, Types, And Functions

`testCreateViaConfig()` delegates to `TestSpaceUsageFactory.testCreateViaConfig(DUFactory.class)`. `testParams()` uses `DUFactory.Conf`, `setRefreshPeriod`, `conf.setFromObject`, `new DUFactory().setConfiguration(conf).paramsFor(dir)`, and assertions over params.

## Control Flow

The test writes a one-hour refresh period into `OzoneConfiguration`, creates a factory, asks for params for a temp directory, and checks the source and persistence classes.

## State And Persistence

State is in-memory configuration and a temp directory reference. The params use `SaveSpaceUsageToFile`, but this test does not write the file.

## Dependencies And Integration Points

It integrates `DUFactory`, config object binding, `SpaceUsageCheckFactory.create`, `DU`, and `SaveSpaceUsageToFile`.

## Risks

The test checks exact runtime classes, so subclassing or decorator changes will need intentional updates. It does not validate the path or expiry details of `SaveSpaceUsageToFile`.

## Test Signals

Signals include configured factory class selection, correct directory identity, exact refresh duration, `DU` source class, and `SaveSpaceUsageToFile` persistence class.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDUFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDUOptimized.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDUOptimized.java

## Purpose

This test class verifies `DUOptimized` delegation and optional container-usage aggregation.

## Important APIs, Types, And Functions

The subject is `DUOptimized`. A mocked `DU` is injected into the private `metaPathDU` field via reflection. Tests call `getUsedSpace`, `setContainerUsedSpaceProvider`, `getCapacity`, and `getAvailable`.

## Control Flow

`setUp()` creates a subject with `/tmp` paths and replaces its internal `DU`. Tests configure mock return values and assert delegation. When a container usage provider is set, used space is the sum of metadata DU usage and the supplied container usage.

## State And Persistence

State is in-memory subject fields and mock behavior. No real filesystem state is measured despite `/tmp` constructor arguments.

## Dependencies And Integration Points

The test integrates with Mockito, reflection, `Supplier<Long>`, production `DU`, and `DUOptimized`.

## Risks

Reflection creates brittle coupling to the private field name `metaPathDU`. The test covers arithmetic and delegation, not exclusion provider path handling or real disk behavior.

## Test Signals

Signals are exact used-space delegation, additive container usage, capacity delegation, and available-space delegation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDUOptimized.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDUOptimizedFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDUOptimizedFactory.java

## Purpose

This class tests that `DUOptimizedFactory` creates params using the optimized disk-usage source, configured refresh period, and file persistence.

## Important APIs, Types, And Functions

The test uses `DUFactory.Conf`, `OzoneConfiguration`, `DUOptimizedFactory.setConfiguration`, and `paramsFor(File, Supplier<File>)`. It asserts `SpaceUsageCheckParams` contents.

## Control Flow

The test writes a 30-minute refresh into configuration, creates the factory, supplies an exclusion file provider, and obtains params for a temp directory.

## State And Persistence

Only configuration and temp path references are held. The resulting persistence class is `SaveSpaceUsageToFile`, but no actual save/load occurs.

## Dependencies And Integration Points

It integrates with `DUOptimizedFactory`, shared `DUFactory.Conf`, `DUOptimized`, and `SaveSpaceUsageToFile`.

## Risks

The test confirms class wiring but not whether the exclusion provider is later honored by `DUOptimized`. Exact-class assertions may need updates for wrapper implementations.

## Test Signals

Signals are correct directory identity, refresh duration, `DUOptimized` source class, and `SaveSpaceUsageToFile` persistence class.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDUOptimizedFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDedicatedDiskSpaceUsage.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDedicatedDiskSpaceUsage.java

## Purpose

This class tests `DedicatedDiskSpaceUsage` against a real temporary directory with a created file.

## Important APIs, Types, And Functions

It reuses `TestDU.createFile`, constructs `new DedicatedDiskSpaceUsage(dir)`, and asserts `getUsedSpace()`.

## Control Flow

The test writes a 1024-byte file into the temp directory, creates the subject, and asserts that observed used space is at least `FILE_SIZE - 20`, matching a Hadoop Common test tolerance.

## State And Persistence

State is real temporary filesystem content. There is no explicit persistent metadata beyond the temp file.

## Dependencies And Integration Points

The class integrates with JUnit temp directories, `DedicatedDiskSpaceUsage`, `SpaceUsageSource`, and `TestDU`'s file creation helper.

## Risks

The test is environment-sensitive because actual filesystem accounting may differ by platform or mount options. It does not assert capacity or available-space behavior.

## Test Signals

The key signal is `getUsedSpace()` reflecting the created file within the lower-bound tolerance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDedicatedDiskSpaceUsage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDedicatedDiskSpaceUsageFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDedicatedDiskSpaceUsageFactory.java

## Purpose

This test verifies config-based creation and parameter generation for `DedicatedDiskSpaceUsageFactory`.

## Important APIs, Types, And Functions

`testCreateViaConfig()` delegates to the shared factory-selection test. `testParams()` uses `DedicatedDiskSpaceUsageFactory.Conf.configKeyForRefreshPeriod`, writes `2m` into `OzoneConfiguration`, and checks returned `SpaceUsageCheckParams`.

## Control Flow

Configuration is populated, the factory is configured, params are requested for a temp dir, and assertions inspect directory, refresh, and source class.

## State And Persistence

State is only in-memory configuration and temp path. The test does not exercise persistence behavior.

## Dependencies And Integration Points

It integrates with `SpaceUsageCheckFactory.create`, `DedicatedDiskSpaceUsageFactory`, `DedicatedDiskSpaceUsage`, and duration parsing through Ozone config.

## Risks

Exact duration parsing and exact source class are guarded, but persistence class is not checked here. Changes in default persistence could slip through this test.

## Test Signals

Signals include configured factory selection, `Duration.ofMinutes(2)`, directory identity, and `DedicatedDiskSpaceUsage` source class.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDedicatedDiskSpaceUsageFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestSaveSpaceUsageToFile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestSaveSpaceUsageToFile.java

## Purpose

This class tests file-backed space-usage persistence, including valid saves, invalid values, expiry, missing data, garbage content, missing files, and overwrite behavior.

## Important APIs, Types, And Functions

The subject is `SaveSpaceUsageToFile`. Tests call `save(SpaceUsageSource)` and `load()`. Helpers include `saveToFile(String)`, `MockSpaceUsageSource.fixed`, and `GenericTestUtils.waitFor`.

## Control Flow

Each test sets a temp `space_usage.txt` path, constructs persistence with either a long or short expiry, writes through subject or manually, then loads and asserts `OptionalLong` presence/value and file existence.

## State And Persistence

State is actual file content in a temp directory. A valid save writes used-space and timestamp. Invalid zero-used source does not create a file. Expired, malformed, time-missing, and absent files return empty values.

## Dependencies And Integration Points

It integrates with Commons IO file writing, UTF-8 encoding, Java `Instant`/`Duration`, `SpaceUsagePersistence`, and `SpaceUsageSource`.

## Risks

Expiry tests rely on wall-clock timing and `waitFor`, so slow or clock-skewed environments can be flaky. The test assumes the invalid source with used zero should not persist.

## Test Signals

Signals are file creation for valid usage, empty loads for invalid/expired/missing/garbage data, and replacement of existing file content with the latest valid used-space value.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestSaveSpaceUsageToFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestSpaceUsageFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestSpaceUsageFactory.java

## Purpose

This class tests `SpaceUsageCheckFactory.create(ConfigurationSource)` selection, configuration injection, and fallback behavior for broken or invalid factory class settings.

## Important APIs, Types, And Functions

Important helpers are `testCreateViaConfig`, `configFor`, `assertCreatesDefaultImplementation`, `testDefaultFactoryForBrokenImplementation`, and `testDefaultFactoryForWrongConfig`. Nested classes model broken implementations and a configurable `SpyFactory`.

## Control Flow

Tests populate `configKeyForClassName()` with valid, missing, private, empty, unknown, and non-implementing class values. Factory creation is invoked, then the class, configuration injection, default fallback, and log output are asserted.

## State And Persistence

State is in-memory configuration and captured logs via `LogCapturer`. There is no filesystem persistence.

## Dependencies And Integration Points

The class integrates with `OzoneConfiguration`, `ConfigurationSource`, `SpaceUsageCheckFactory`, logging, reflection-based class loading, and concrete factory tests that reuse `testCreateViaConfig`.

## Risks

The tests depend on log-message inclusion for invalid nonempty config values. They do not call `paramsFor` on successful real factories except through other test classes.

## Test Signals

Signals include correct factory instantiation for valid config, `setConfiguration` being called, default fallback for unusable classes or bad config, no log for empty config, and log mentioning invalid configured class names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestSpaceUsageFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/exceptions/TestSCMExceptionResultCodes.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/exceptions/TestSCMExceptionResultCodes.java

## Purpose

This test guards the positional and name mapping between `SCMException.ResultCodes` and protobuf `ScmBlockLocationProtocolProtos.Status`.

## Important APIs, Types, And Functions

The single `codeMapping()` test compares `ResultCodes.values()` and `Status.values()`, names, ordinals, and reverse conversion by ordinal.

## Control Flow

The test first asserts both enums have equal length, then iterates by index and requires matching names and ordinal-derived conversion.

## State And Persistence

There is no mutable state. The persistence concern is compatibility of enum ordering in generated protobuf and Java exception code.

## Dependencies And Integration Points

It integrates Java enum constants with protobuf-generated status constants used in SCM block-location RPC responses.

## Risks

This is intentionally brittle: adding, removing, or reordering either enum breaks compatibility. Any enum evolution must preserve ordering or include explicit migration/translation.

## Test Signals

The signal is exact length, name, and ordinal alignment for every result/status constant.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/exceptions/TestSCMExceptionResultCodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAUtils.java

## Purpose

This test verifies that `SCMHAUtils.removeSelfId` removes the current SCM node ID from HA node lists in configuration.

## Important APIs, Types, And Functions

It uses `OZONE_SCM_SERVICE_IDS_KEY`, `OZONE_SCM_NODES_KEY`, `OZONE_SCM_NODE_ID_KEY`, `SCMHAUtils.removeSelfId`, and `HddsUtils.getSCMNodeIds`.

## Control Flow

The test constructs a config with service `mySCM`, nodes `scm1,scm2,scm3`, and self ID `scm3`, calls `removeSelfId`, then reads the resulting node list.

## State And Persistence

State is an in-memory `OzoneConfiguration`. No persistent HA metadata is modified.

## Dependencies And Integration Points

It integrates SCM HA config keys, HDDS config parsing, and utility behavior used when excluding the local SCM from peer operations.

## Risks

The test covers one service and one self ID only. Multi-service configs, whitespace variations, and absent IDs rely on other coverage.

## Test Signals

Signals are exactly two remaining nodes and absence of the self ID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSequenceIdType.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSequenceIdType.java

## Purpose

This class protects `SequenceIdType` enum names because they are persisted RocksDB keys.

## Important APIs, Types, And Functions

`testStringSyncWithEnumConstants()` asserts exact enum `name()` strings, including the deprecated or unusual casing `CertificateId`. `testIfNewEnumConstantGetsAdded()` compares the current enum set against an expected set and emits a compatibility-focused failure message.

## Control Flow

Tests enumerate constants, compute added/removed names relative to expected, and fail if any change is detected.

## State And Persistence

There is no runtime mutable state. The state being protected is persisted sequence-id key names in RocksDB.

## Dependencies And Integration Points

The file integrates with SCM HA sequence ID storage and any code that reads/writes counters keyed by `SequenceIdType.name()`.

## Risks

Any intentional enum addition/removal or rename requires explicit backward-compatibility analysis and test update. The guard does not verify database migration logic directly.

## Test Signals

Signals are exact enum-name equality and empty added/removed sets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSequenceIdType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestNetworkTopologyImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestNetworkTopologyImpl.java

## Purpose

This large test suite validates `NetworkTopologyImpl` behavior across multiple topology schemas, including membership, path resolution, add/remove/update, random selection under scopes and exclusions, affinity selection, distance costs, sorting, and ancestor/descendant helpers.

## Important APIs, Types, And Functions

Key production APIs are `NetworkTopology.add`, `remove`, `update`, `contains`, `getNode`, `chooseRandom`, `getNumOfLeafNode`, `getNumOfNodes`, `getNodes`, `isSameParent`, `isSameAncestor`, `getDistanceCost`, `sortByDistanceCost`, `NodeSchemaManager.init`, `NodeImpl`, and `InnerNodeImpl`. Helpers `topologies`, `initNetworkTopology`, `pickNodesAtRandom`, and `pickNodes` generate broad coverage.

## Control Flow

Parameterized tests run over root/leaf, rack, datacenter/rack, datacenter/rack/nodegroup, and region/datacenter/rack/nodegroup schemas. Nodes are added to a fresh cluster, then tests query or mutate the topology. Selection tests run repeated random or sequential picks and assert excluded scopes, excluded nodes, ancestor generation, and affinity constraints.

## State And Persistence

State is in-memory topology tree state inside `NetworkTopologyImpl` and the singleton `NodeSchemaManager`, which each test reinitializes. There is no persistent store, but topology paths encode operational placement state.

## Dependencies And Integration Points

The suite integrates with `NodeSchema`, `NetConstants`, `NetUtils`, schema files under `networkTopologyTestFiles`, Mockito shuffle injection, JUnit parameterization, and SCM network placement logic.

## Risks

Randomized selection tests may be probabilistic, though repeated sequential helpers reduce missed coverage. The singleton schema manager can leak state if tests are reordered or parallelized unsafely. Exact exception message prefixes and distance-cost values are compatibility guards.

## Test Signals

Signals include correct leaf/node counts, invalid-depth rejection, config-file initialization, ancestor logic, inner-node mutation rejection, scoped and inverted-scope selection, exclusion enforcement, affinity confinement, single-node null selection, update semantics, cost calculations, distance sorting, and null-reader shuffle-only behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestNetworkTopologyImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestNodeSchemaLoader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestNodeSchemaLoader.java

## Purpose

This class tests XML network topology schema loading, including valid schemas, missing files, invalid topology definitions, malformed references, unsupported types, invalid versions, and XXE protection.

## Important APIs, Types, And Functions

It uses `NodeSchemaLoader.getInstance().loadSchemaFromFile`, parameterized `getSchemaFiles`, `getClassloaderResourcePath`, and `assertMessageContains`.

## Control Flow

Parameterized tests map fixture filenames to expected error substrings, load each fixture from `networkTopologyTestFiles`, and assert `IllegalArgumentException`. Separate tests load `good.xml` successfully and require `FileNotFoundException` for a derived missing filename.

## State And Persistence

No mutable state is persisted. Test inputs are classpath XML resources.

## Dependencies And Integration Points

The tests integrate with XML schema fixtures, JUnit parameterization, classloader resource resolution, and topology schema parsing used by SCM network placement.

## Risks

Assertions depend on specific error-message substrings. The external-entity case is a security regression guard and should remain explicit if XML parser internals change.

## Test Signals

Signals include successful parse for `good.xml`, expected failures for every invalid fixture, missing-file exception, and rejection of external entity declarations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestNodeSchemaLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestNodeSchemaManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestNodeSchemaManager.java

## Purpose

This test verifies `NodeSchemaManager` initialization from config, layer-cost access, schema-load failure handling, and topology path completion defaults.

## Important APIs, Types, And Functions

It uses `NodeSchemaManager.getInstance`, `init(OzoneConfiguration)`, `getCost`, `getMaxLevel`, and `complete`. Config key `OZONE_SCM_NETWORK_TOPOLOGY_SCHEMA_FILE` points to `good.xml`.

## Control Flow

The constructor initializes the singleton manager from `good.xml`. Tests check invalid cost levels, valid max level and costs, failure when the schema path is invalid, and completion of partial paths by adding default rack/nodegroup components.

## State And Persistence

State lives in the singleton manager and in-memory configuration. There is no persistence.

## Dependencies And Integration Points

The test integrates with default rack/nodegroup constants, XML topology fixtures, and SCM configuration parsing.

## Risks

Singleton state means constructor-side initialization is shared across tests. The path-completion assertions are tied to the schema shape in `good.xml`.

## Test Signals

Signals include exceptions for levels 0 and max+1, max level 4, allowed costs 0 or 1, runtime failure for missing schema path, completed default rack/nodegroup paths, and null for an uncompletable datacenter-prefixed path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestNodeSchemaManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestYamlSchemaLoader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestYamlSchemaLoader.java

## Purpose

This class tests YAML topology schema loading, including invalid root/leaf layouts, a valid fixture, missing files, and the default YAML schema.

## Important APIs, Types, And Functions

It uses `NodeSchemaLoader.getInstance().loadSchemaFromFile`, fixture paths under `networkTopologyTestFiles`, and `NodeSchemaLoader.NodeSchemaLoadResult`.

## Control Flow

Parameterized tests load invalid YAML fixtures and assert expected message substrings. Other tests assert `good.yaml` loads, a missing file throws `FileNotFoundException`, and `network-topology-default.yaml` produces three schema entries.

## State And Persistence

No state persists beyond parsed schema results. Inputs are classpath YAML resources.

## Dependencies And Integration Points

The tests integrate with YAML parsing support in `NodeSchemaLoader` and the default network topology resource shipped with the framework.

## Risks

The tests cover only two invalid YAML layouts and do not duplicate all XML validation cases. Message substring checks are brittle but useful for targeted diagnostics.

## Test Signals

Signals include rejection of multiple-root and middle-leaf schemas, successful good/default YAML loads, missing-file failure, and default schema size of three.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/scm/net/TestYamlSchemaLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestGrpcTlsConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestGrpcTlsConfig.java

## Purpose

This class tests TLS protocol and cipher-suite enforcement for Ozone gRPC endpoints using Netty gRPC with mutual TLS.

## Important APIs, Types, And Functions

It uses `CertificateClientTestImpl`, `NettyServerBuilder`, `NettyChannelBuilder`, `GrpcSslContexts`, `SslContextBuilder`, `SslProvider.JDK`, `ClientAuth.REQUIRE`, `SupportedCipherSuiteFilter`, and the generated `XceiverClientProtocolServiceGrpc` stub. Helpers are `setupServer`, `setupClient`, `sendRequest`, and `shutdown`.

## Control Flow

Each test starts an ephemeral TLS server, builds a TLS client with selected protocols/ciphers, sends a create-container request through a streaming RPC, and asserts success or `ExecutionException`. The fake service replies with `ContainerProtos.Result.SUCCESS`.

## State And Persistence

State is runtime TLS context state, certificate/key material from `CertificateClientTestImpl`, gRPC server/channel objects, and a `CompletableFuture` for response capture. Nothing persists to disk.

## Dependencies And Integration Points

The suite integrates HDDS security config, generated datanode container protobuf/gRPC APIs, pipeline/test request builders, Ratis-shaded gRPC/Netty, and certificate managers.

## Risks

TLS 1.3 and cipher availability depends on JDK/provider support. Unsupported cipher filtering is explicitly tested server-side. The test uses localhost networking and can be sensitive to async failure timing.

## Test Signals

Signals include TLS 1.3 success, TLS 1.2 rejection against TLS 1.3-only server, matching cipher success, mismatched cipher failure, default TLS config success, and successful filtering of a fake configured server cipher.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestGrpcTlsConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestReloadingX509KeyManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestReloadingX509KeyManager.java

## Purpose

This test verifies that `ReloadingX509KeyManager` updates its private key when the certificate client renews key material and emits exactly one reload log entry.

## Important APIs, Types, And Functions

It uses `CertificateClientTestImpl.getKeyManager`, `getPrivateKey`, `renewRootCA`, `renewKey`, `ReloadingX509KeyManager.getPrivateKey`, and `LogCapturer`.

## Control Flow

The test obtains the initial key manager and private key, verifies lookup by component alias, renews the root CA and leaf key, verifies a different private key is returned from the same key manager, and inspects reload logs.

## State And Persistence

State lives in the test certificate client, key manager keystore contents, and captured logs. No disk persistence is used.

## Dependencies And Integration Points

It integrates certificate notification callbacks from `CertificateClientTestImpl` with the SSL key manager reload path.

## Risks

The alias convention `componentName + "_key"` is a coupling point. Log-count assertions are sensitive to logging changes and shared static certificate client setup.

## Test Signals

Signals are initial key equality, renewed key inequality, updated manager key equality, presence of reload log text, and exactly one reload.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestReloadingX509KeyManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestReloadingX509TrustManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestReloadingX509TrustManager.java

## Purpose

This test verifies that `ReloadingX509TrustManager` expands accepted issuers after root CA renewal and reloads once.

## Important APIs, Types, And Functions

It uses `CertificateClientTestImpl.getTrustManager`, `getRootCACertificate`, `renewRootCA`, `renewKey`, `ReloadingX509TrustManager.getAcceptedIssuers`, and log capture.

## Control Flow

The test obtains a trust manager, asserts only the initial root CA is accepted, renews root CA and leaf key, then asserts both old and new root certificates are accepted and one reload was logged.

## State And Persistence

State is the in-memory root certificate set, trust manager keystore, and captured logs. Nothing persists to disk.

## Dependencies And Integration Points

It validates certificate notification integration between test certificate client and SSL trust manager.

## Risks

The test assumes root CA rotation appends trust rather than replacing it. Log text and count are brittle but intentional reload signals.

## Test Signals

Signals are accepted-issuer set before and after rotation, root certificate inequality, reload log presence, and exactly one reload event.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestReloadingX509TrustManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestSSLConnectionWithReload.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestSSLConnectionWithReload.java

## Purpose

This integration-style test verifies that a gRPC mutual-TLS connection continues working after the certificate client renews its key and reload-capable managers update.

## Important APIs, Types, And Functions

It uses `CertificateClientTestImpl`, `SecurityConfig.getGrpcSslProvider`, Netty gRPC builders, `GrpcSslContexts`, `ReloadingX509KeyManager`/trust manager through the certificate client, and generated container RPC stubs. Helpers are `setupServer`, `setupClient`, `sendRequest`, and the nested fake `GrpcService`.

## Control Flow

The test starts a TLS server and client, sends a create-container request successfully, calls `caClient.renewKey()`, sleeps for `RELOAD_INTERVAL`, and sends another request over the same channel expecting success.

## State And Persistence

State is in-memory certificate/key material, SSL contexts, gRPC connection state, and futures. `KeyStoresFactory` variables are declared but remain null in this implementation.

## Dependencies And Integration Points

It integrates HDDS certificate reload notifications, Netty TLS, gRPC streaming RPCs, and container command protobufs.

## Risks

The fixed sleep is timing-sensitive and may be slow or flaky. Existing TLS sessions may not fully renegotiate depending on provider behavior, so the test primarily guards practical request continuity.

## Test Signals

Signals are `SUCCESS` responses before and after key renewal, and clean shutdown of channel/server.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/ssl/TestSSLConnectionWithReload.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyTestUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyTestUtil.java

## Purpose

This test utility generates `ManagedSecretKey` instances for symmetric-key tests.

## Important APIs, Types, And Functions

`generateKey(String, Instant, Duration)` creates a JCA `KeyGenerator` for the requested algorithm, generates a `SecretKey`, assigns a random UUID, and builds a `ManagedSecretKey` with creation and expiry times. `generateHmac` specializes this to `HmacSHA256`.

## Control Flow

Callers request a key for a creation time and validity duration. The utility computes expiry as `creationTime.plus(validDuration)`.

## State And Persistence

The utility is stateless. Generated keys are in-memory only and are not stored.

## Dependencies And Integration Points

It integrates with JCA `KeyGenerator`, `SecretKey`, UUIDs, and the production `ManagedSecretKey` type.

## Risks

Algorithms must be available in the active JCA provider. Random IDs and key material mean tests should not compare generated keys except where explicitly captured.

## Test Signals

Signals are indirect: generated keys can sign/verify, expire at expected times, and match requested algorithms.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/TestLocalKeyStore.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/TestLocalKeyStore.java

## Purpose

This class tests `LocalSecretKeyStore` JSON persistence, file permissions, overwrite semantics, and backward-compatible loading of existing key-store schema.

## Important APIs, Types, And Functions

It uses `SecretKeyStore.save`, `load`, `LocalSecretKeyStore`, `ManagedSecretKey`, JCA `KeyGenerator`, `SecretKeySpec`, Base64 decoding, and POSIX file permission checks.

## Control Flow

Setup creates a temp JSON file and store. Parameterized save/load tests cover empty, single, and multiple keys. `testOverwrite()` saves one list then another. `testLoadExistingFile()` writes a literal historical JSON payload and compares the loaded key fields.

## State And Persistence

State is persisted in the temp JSON file. Saved files must exist and have owner read/write permissions only. Key fields include UUID, creation/expiry time, algorithm, and encoded secret key bytes.

## Dependencies And Integration Points

The test integrates Guava collection helpers, Java NIO permissions, JCA crypto, and the symmetric key persistence layer used by secret-key managers.

## Risks

POSIX permission checks can fail on non-POSIX filesystems. The existing-file JSON is a backward-compatibility fixture and should not be changed casually.

## Test Signals

Signals include exact reloaded key fields, secure file permissions, overwrite replacing prior keys, and successful load of the hard-coded historical JSON.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/TestLocalKeyStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/TestManagedSecretKey.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/TestManagedSecretKey.java

## Purpose

This class tests `ManagedSecretKey` signing and signature verification for raw bytes, protobuf transfer, and block token identifiers.

## Important APIs, Types, And Functions

It uses `ManagedSecretKey.sign(byte[])`, `sign(TokenIdentifier)`, `isValidSignature`, `toProtobuf`, `fromProtobuf`, `SecretKeyTestUtil.generateHmac`, `OzoneBlockTokenIdentifier`, `BlockID`, and access-mode enums.

## Control Flow

The success test signs random data, verifies with the same key and a protobuf-round-tripped key, then signs a block token and verifies it the same way. The failure test verifies random signatures fail and signatures from one key cannot be verified by another.

## State And Persistence

State is in-memory key material and token identifiers. Protobuf conversion tests serialization fidelity but not disk persistence.

## Dependencies And Integration Points

The class integrates symmetric HMAC keys with HDDS token signing and protobuf exchange.

## Risks

Random test data and key material make failures dependent on crypto implementation behavior but should be deterministic in pass/fail. The test does not cover expired-key checks.

## Test Signals

Signals are successful raw/token verification by same and transferred keys, rejection of random signatures, and rejection by a different key.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/TestManagedSecretKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/TestSecretKeyManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/TestSecretKeyManager.java

## Purpose

This class tests `SecretKeyManager` initialization and rotation behavior over saved key sets of different ages.

## Important APIs, Types, And Functions

It uses `SecretKeyManager.checkAndInitialize`, `checkAndRotate`, `SecretKeyStateImpl`, `SecretKeyStore.load/save`, `ManagedSecretKey`, `SecretKeyTestUtil.generateKey`, and Mockito `ArgumentCaptor`.

## Control Flow

Parameterized load cases simulate first start, restart, and multi-day downtime. The manager either loads retained keys and current key or generates a new key. Rotation cases set initial state, run rotation, then assert whether a new current key was generated, expired keys filtered, and saved state updated.

## State And Persistence

State lives in `SecretKeyStateImpl` and mocked store interactions. Persisted state is represented by lists returned from or captured by the mock `SecretKeyStore`.

## Dependencies And Integration Points

The tests integrate key lifecycle durations, key-store persistence, sorted secret-key state, and HMAC key generation.

## Risks

Time comparisons allow minute-level tolerance; boundary behavior around exact rotation/expiry instants should be reviewed carefully. Parameterized cases mutate expected retained lists by adding the new key, so reused list instances would be risky.

## Test Signals

Signals include new-key generation on empty/fully expired stores, retained key filtering, no rotation for fresh current key, rotation for old current key, persisted rotated key set, correct algorithm, near-now creation time, and expected expiry.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/symmetric/TestSecretKeyManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestBlockTokenVerifier.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestBlockTokenVerifier.java

## Purpose

This class specializes the abstract token-verifier test matrix for `BlockTokenVerifier`.

## Important APIs, Types, And Functions

It overrides `tokenEnabledConfigKey`, `newTestSubject`, `unverifiedRequest`, `verifiedRequest`, and `newTokenId`. It uses `HDDS_BLOCK_TOKEN_ENABLED`, `BlockTokenVerifier`, `OzoneBlockTokenIdentifier`, `MockPipeline`, close-container requests, write-chunk requests, `BlockID`, and all block access modes.

## Control Flow

The inherited tests build enabled/disabled security config, create verified and unverified container commands, create a signed token through the mock secret manager, and exercise verification paths. For block tokens, close-container is treated as unverified, while write-chunk requires a block token.

## State And Persistence

State is in-memory token identifiers with a fixed test secret key UUID and future expiry. No persistence is used.

## Dependencies And Integration Points

It integrates block-token verification with container command request classification and shared short-lived token verification behavior.

## Risks

Coverage depends on inherited tests; this class only defines block-specific fixtures. The verified request uses a fixed block ID matching the token service.

## Test Signals

Signals include inherited checks for disabled verification, skipped unrelated commands, expired key rejection, missing key rejection, invalid signature rejection, expired token rejection, and valid block-token acceptance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestBlockTokenVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestContainerTokenVerifier.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestContainerTokenVerifier.java

## Purpose

This class specializes the abstract token-verifier test matrix for `ContainerTokenVerifier`.

## Important APIs, Types, And Functions

It overrides token fixture methods for `HDDS_CONTAINER_TOKEN_ENABLED`, `ContainerTokenVerifier`, `ContainerTokenIdentifier`, create-container requests, and write-chunk requests. `AtomicLong CONTAINER_ID` gives each token/request a unique container ID.

## Control Flow

Inherited tests build token-enabled/disabled configs and verify behavior. For container tokens, write-chunk is treated as unrelated/unverified, while create-container requires a token for the incremented container ID.

## State And Persistence

State is in-memory token IDs and an atomic counter. There is no persistence.

## Dependencies And Integration Points

It integrates container-token verification with datanode container command classification, `ContainerID`, and the shared token verifier test base.

## Risks

The atomic counter is static, so generated IDs increase across test invocations. This is useful for uniqueness but can surprise tests that assume fixed IDs.

## Test Signals

Signals are the inherited token verifier matrix applied to container-token-specific commands and identifiers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestContainerTokenVerifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestOzoneBlockTokenIdentifier.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestOzoneBlockTokenIdentifier.java

## Purpose

This class tests `OzoneBlockTokenIdentifier` signing, invalid-signature rejection, Hadoop token URL encoding/decoding, protobuf field reading, equality, and max-length preservation.

## Important APIs, Types, And Functions

It uses `OzoneBlockTokenIdentifier`, `ManagedSecretKey`, `SecretKeyTestUtil.generateHmac`, Hadoop `Token`, `Text`, `readFields`, `getBytes`, `getKind`, `getMaxLength`, and access-mode enums.

## Control Flow

Setup creates a future expiry time and HMAC key. `testSignToken()` signs a token identifier and verifies valid and random signatures. `testTokenSerialization()` embeds identifier/password in a Hadoop token, URL-encodes/decodes it, reads a new identifier from the decoded bytes, and verifies equality and signature.

## State And Persistence

State is in-memory token bytes, signatures, and encoded string. No disk persistence is used, but serialization compatibility is validated.

## Dependencies And Integration Points

The test integrates HDDS block token identifiers with Hadoop security token transport encoding and symmetric signature verification.

## Risks

The expiry setup uses `Time.monotonicNow()` while other tests use wall-clock `Instant`; token semantics must remain compatible with the identifier implementation. Random invalid signatures should never verify.

## Test Signals

Signals include true verification for signed bytes, false verification for random bytes, decoded identifier equality, max-length equality, and valid decoded token password verification.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestOzoneBlockTokenIdentifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestOzoneBlockTokenSecretManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestOzoneBlockTokenSecretManager.java

## Purpose

This class tests block-token generation, identifier creation, service binding to blocks, read/write access enforcement, and expired signing-key rejection.

## Important APIs, Types, And Functions

It uses `OzoneBlockTokenSecretManager`, `BlockTokenVerifier`, `OzoneBlockTokenIdentifier`, `SecretKeySignerClient`, `SecretKeyVerifierClient`, `ManagedSecretKey`, `ContainerTestHelper` request builders, `MockPipeline`, `BlockID`, and access-mode enums.

## Control Flow

Setup creates a pipeline, token-enabled security config, valid secret key, mocked signer/verifier clients, secret manager, and verifier. Tests generate tokens, decode identifiers, verify signatures, build write/put/get/read commands, and assert either successful verification or `BlockTokenException` with expected messages.

## State And Persistence

State is in-memory secret key material, token identifiers, Hadoop tokens, and mocked key-client responses. The temp metadata directory config is set but not central to the tests.

## Dependencies And Integration Points

The suite integrates token signing with datanode command authorization, block service strings, pipeline request builders, and secret-key validity checks.

## Risks

The test uses mocked key clients, so it does not cover network retrieval of secret keys. Error-message assertions are intentionally coupled to verifier diagnostics.

## Test Signals

Signals include correct token service/access modes/key ID/signature, valid put-block use for matching block, rejection for other block, read-only token rejecting write and allowing read, write-only token rejecting read and allowing write, and expired secret-key rejection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TestOzoneBlockTokenSecretManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TokenVerifierTests.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TokenVerifierTests.java

## Purpose

This abstract base class defines common behavioral tests for `ShortLivedTokenVerifier` implementations, shared by block and container token verifiers.

## Important APIs, Types, And Functions

Subclasses provide `newTestSubject`, `tokenEnabledConfigKey`, `unverifiedRequest`, `verifiedRequest`, and `newTokenId`. The base uses `SecurityConfig`, `SecretKeyVerifierClient`, `ManagedSecretKey`, `ShortLivedTokenSecretManager`, Hadoop `Token`, and nested `MockTokenManager`.

## Control Flow

Tests construct enabled or disabled security configs, mock secret-key lookup/verification behavior, generate tokens with fixed mock passwords, and call `TokenVerifier.verify`. They assert skipped verification when disabled or for unrelated commands, and rejection for expired secret keys, unknown key IDs, invalid signatures, and expired tokens. A final test accepts a valid token.

## State And Persistence

State is in-memory token IDs, mocked secret keys, and generated Hadoop tokens. No persistence is used. `SECRET_KEY_ID` is a static random UUID used by subclass token IDs.

## Dependencies And Integration Points

The base ties verifier implementations to HDDS security config keys, short-lived token identifier expiry semantics, and symmetric secret-key verification.

## Risks

Because signatures are mocked, the base checks verifier orchestration rather than cryptographic correctness. Subclasses must ensure their `verifiedRequest` truly requires their token type.

## Test Signals

Signals include no key lookup for disabled/unrelated cases, `BlockTokenException` messages for expired key, missing key, invalid signature, and expired token, plus no exception for valid token verification.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TokenVerifierTests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/package-info.java

## Purpose

This package-info file documents that the package contains block-token-related classes.

## Important APIs, Types, And Functions

It declares the `org.apache.hadoop.hdds.security.token` test package and provides package Javadoc only.

## Control Flow

There is no executable control flow.

## State And Persistence

No state or persistence exists.

## Dependencies And Integration Points

The file integrates with Java package documentation for token tests.

## Risks

The comment is slightly narrow because the package also contains container-token verifier tests; documentation may need broadening if maintained.

## Test Signals

Compilation is the only signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/MockCAStore.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/MockCAStore.java

## Purpose

This class is a no-op `CertificateStore` implementation used by CA tests that need a store dependency without metadata persistence.

## Important APIs, Types, And Functions

It implements `storeValidCertificate`, `checkValidCertID`, `storeValidScmCertificate`, `removeAllExpiredCertificates`, `getCertificateByID`, `listCertificate`, and `reinitialize`. Most methods do nothing; list methods return empty collections and lookup returns null.

## Control Flow

Production CA code can call store methods during tests, but the mock absorbs writes and reports no stored certificates.

## State And Persistence

There is no state and no persistence. Calls do not record certificates or serial IDs.

## Dependencies And Integration Points

It integrates with `DefaultCAServer` tests, `CertificateStore`, `NodeType`, `X509Certificate`, and `SCMMetadataStore`.

## Risks

Because it ignores all writes, it cannot test duplicate serial handling, certificate listing, expiry cleanup, or metadata-store reinitialization. Tests using it validate CA control flow rather than storage semantics.

## Test Signals

Signals are indirect: CA tests proceed without store failures while storage-sensitive behavior remains unverified.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/MockCAStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/TestDefaultCAServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/TestDefaultCAServer.java

## Purpose

This test suite validates `DefaultCAServer` initialization, root and subordinate CA behavior, certificate requests, CSR subject validation, external root CA loading, certificate-chain loading, subordinate initialization, and certificate durations across daylight saving time.

## Important APIs, Types, And Functions

It uses `DefaultCAServer`, `CertificateServer`, `CertificateApprover.ApprovalType.TESTING_AUTOMATIC`, `DefaultProfile`, `DefaultCAProfile`, `SCMCertificateClient`, `CertificateCodec`, `CertificateSignRequest`, `SelfSignedCertificate`, `HDDSKeyGenerator`, `KeyStorage`, and security config keys for metadata and external root CA material.

## Control Flow

Each test builds temp-backed `OzoneConfiguration`, `SecurityConfig`, and `MockCAStore`. Root init creates or loads CA material and is checked for idempotence. Request tests generate CSRs, call `requestCertificate`, wait on completed futures, and inspect returned `CertPath`. External CA tests write key/cert material to configured locations before init. Subordinate CA tests first obtain/store a certificate from root CA, then initialize an SCM CA.

## State And Persistence

State includes temp metadata directories, generated key pairs, certificates written through `CertificateCodec` and `KeyStorage`, and no-op store behavior. External root and chain tests exercise file-backed certificate/key discovery.

## Dependencies And Integration Points

The suite integrates Bouncy Castle CSR/cert utilities, HDDS security config, SCM certificate client layout, CA profiles, Java certificate paths, and X.509 duration settings.

## Risks

The mock store omits real certificate persistence checks. Several tests rely on exact exception messages, wall-clock dates, timezone mutation, and random IDs. The daylight-saving test changes the JVM default timezone and must restore it to avoid cross-test leakage.

## Test Signals

Signals include non-null/idempotent CA certs, missing-cert/key initializer failures, cert path ordering with CA at index 1, issuer/subject linkage, invalid subject rejection, subordinate empty failure, external cert and chain selection, successful subordinate init, and exact max-duration milliseconds across DST.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/TestDefaultCAServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/TestDefaultProfile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/TestDefaultProfile.java

## Purpose

This class tests the default PKI profile and approver validation for supported subject alternative names, CSR signature verification, CA constraints, SAN criticality, unsupported SAN types, and extended key usage.

## Important APIs, Types, And Functions

It uses `DefaultProfile`, `DefaultApprover`, `CertificateSignRequest.Builder`, `HDDSKeyGenerator`, Bouncy Castle `PKCS10CertificationRequest`, `ExtensionsGenerator`, `GeneralName`, `Extension.subjectAlternativeName`, `ExtendedKeyUsage`, and `KeyPurposeId`.

## Control Flow

Setup creates temp-backed security config, a profile, approver, and key pair. Tests generate valid CSRs through Ozone's builder or manually build CSRs with selected extensions. Assertions call `isSupportedGeneralName`, `verifyPkcs10Request`, and `verfiyExtensions`.

## State And Persistence

State is in-memory key pairs, CSRs, extensions, and security config. No certificates are persisted.

## Dependencies And Integration Points

The suite integrates certificate request construction with CA profile validation rules used by `DefaultCAServer`.

## Risks

The helper `getInvalidCSR` ignores its `kPair` parameter and uses the field `keyPair`, which is harmless here but misleading. The method name `verfiyExtensions` reflects production spelling. Criticality and supported-name assertions are policy guards that require intentional updates when profile rules change.

## Test Signals

Signals include support for IP, DNS, and otherName; rejection of directory and email names; valid CSR signature; invalid key-pair signature failure; valid normal extensions; CA extension rejection; email/URI SAN rejection; critical DNS rejection with noncritical DNS acceptance; client/server EKU acceptance; critical clientAuth and OCSP EKU rejection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/TestDefaultProfile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/package-info.java

## Purpose

This package-info file documents that the package contains tests for the default CA.

## Important APIs, Types, And Functions

It declares the test package and package-level Javadoc only.

## Control Flow

There is no executable control flow.

## State And Persistence

No state or persistence exists.

## Dependencies And Integration Points

The file integrates with Java package documentation for CA authority tests.

## Risks

Risk is limited to stale documentation as the package grows.

## Test Signals

Compilation is the only signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/CertificateClientTestImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/CertificateClientTestImpl.java

## Purpose

This test-only `CertificateClient` implementation creates in-memory root and leaf certificates, exposes reloadable key/trust managers, supports key/root renewal, and provides enough certificate-client behavior for SSL and CA tests.

## Important APIs, Types, And Functions

Key methods include constructors with optional auto-renew, `getPrivateKey`, `getPublicKey`, `getCertificate`, `getTrustChain`, `getCACertificate`, `verifySignature`, `getRootCACertificate`, `getAllRootCaCerts`, `renewRootCA`, `renewKey`, `getKeyManager`, `getTrustManager`, `createClientTrustManager`, `registerNotificationReceiver`, and `close`. Nested `RenewCertTask` triggers root and leaf renewal.

## Control Flow

Construction generates key pairs, creates a self-signed root CA, signs a leaf certificate with `DefaultApprover`, populates certificate maps/sets, and optionally schedules renewal for the configured grace-period start. `renewKey()` generates a new leaf cert, swaps active key/cert, stores it, and notifies registered managers. Key/trust managers are lazily created and registered as notification receivers.

## State And Persistence

State is in-memory: key pairs, current leaf certificate, current/root CA certs, certificate map, notification receivers, and optional scheduled executor. No keys or certs are written to disk.

## Dependencies And Integration Points

It integrates HDDS `SecurityConfig`, key generation, self-signed certificate generation, CSR building/signing, reloadable SSL managers, client trust manager provider callbacks, and certificate notification APIs.

## Risks

It is intentionally incomplete: `getCertPath`, `initWithRecovery`, and root-rotation listener behavior are stubbed. The notification receiver set is a `HashSet` with synchronized writes but unsynchronized iteration during renewal. Auto-renew scheduling depends on wall clock and should be used carefully in tests.

## Test Signals

Signals include valid generated key/cert chain, signature verification, key manager reload after `renewKey`, trust manager issuer expansion after `renewRootCA`, notification delivery with old/new serials, and executor shutdown on close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/CertificateClientTestImpl.java -->
