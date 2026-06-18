# subset-b-007385 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfServlet.java

## Purpose

`TestConfServlet` validates the HTTP-facing `ConfServlet` configuration dump endpoint. It exercises content negotiation, property filtering by request parameter, JSON/XML serialization, not-found behavior, invalid output formats, and masking of sensitive configuration values before they reach the servlet response.

## Important APIs and types

- `ConfServlet.parseAcceptHeader(HttpServletRequest)` maps `Accept` headers to `ConfServlet.FORMAT_XML` or `ConfServlet.FORMAT_JSON`.
- `ConfServlet.writeResponse(Configuration, Writer, String)` serializes a Hadoop `Configuration` as XML or JSON and throws `ConfServlet.BadFormatException` for unsupported formats.
- `ConfServlet.doGet(...)` reads `HttpServer2.CONF_CONTEXT_ATTRIBUTE` from the servlet context, consults request parameter `name`, and writes or errors through `HttpServletResponse`.
- Test helpers build `Configuration` instances with normal keys and YARN SQL username/password keys that should be redacted.
- Mockito provides servlet request/response/context doubles; Jetty `JSON.parse` and secure DOM parsing validate response structure.

## Control flow

`initTestProperties` seeds shared normal property maps, accepted content-type mappings, and sensitive properties. `testParseHeaders` loops over representative `Accept` values and checks the servlet's selected format.

`verifyGetProperty` initializes a servlet with a mocked context, sets the request `Accept` header and `name` parameter, invokes `doGet`, and inspects the captured response writer. A null or empty `name` expects all normal properties; a known property expects only that property; an unknown property expects `sendError(SC_NOT_FOUND, ...)`.

`testWriteJson` and `testWriteXml` bypass the servlet request path and directly validate `writeResponse` output. JSON is parsed into the expected `"properties"` array and XML is parsed through `XMLUtils.newSecureDocumentBuilderFactory`. `testBadFormat` ensures unsupported formats produce no partial output. `verifyReplaceProperty` repeats the servlet path for sensitive keys and checks that the original secret value is absent.

## State and persistence behavior

The tests are in-memory. The servlet uses a `Configuration` stored on the servlet context; response content is accumulated in `StringWriter`. Static maps are mutated once before all tests. No filesystem persistence or external server is started.

## Dependencies and integration points

The file integrates `ConfServlet` with `HttpServer2`'s configuration context attribute, servlet APIs, Hadoop `Configuration`, Guava HTTP header constants and string helpers, Jetty JSON parsing, secure XML parsing utilities, JUnit 5, and Mockito. It is a regression surface for admin web UI/configuration endpoints where exposing or filtering configuration values is security-sensitive.

## Risks and edge cases

- Header parsing currently treats unknown, null, plain text, and XML-ish headers as XML; clients with more complex `Accept` negotiation are not covered.
- The property filtering assertions use substring checks, so formatting changes could produce false positives if one key/value appears inside another.
- Redaction checks only verify that the original sensitive value is absent, not the exact replacement token in every output format.
- The mocked servlet setup does not validate actual HTTP content type headers, response status on successful requests, or container lifecycle details.

## Test signals

Strong signals are the matrix of XML/JSON output, null/empty/specific/missing property names, direct JSON/XML parse validation, explicit bad-format rejection, and sensitive-value absence checks for both output formats. Gaps include weighted `Accept` headers, malformed XML/JSON output handling, exact redaction token validation, and end-to-end servlet container tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigRedactor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigRedactor.java

## Purpose

`TestConfigRedactor` verifies Hadoop's default sensitive-configuration key detection. It confirms that `ConfigRedactor` masks common cloud, filesystem, OAuth, SSL, HTTPFS, and Hadoop security secret keys while leaving nearby non-secret configuration names unchanged.

## Important APIs and types

- `ConfigRedactor(Configuration)` builds the redaction policy from a `Configuration`.
- `ConfigRedactor.redact(String key, String value)` returns `"<redacted>"` for sensitive keys and the original value for non-sensitive keys.
- The test runs with `new Configuration()` and `new Configuration(false)` to cover both default resources and an explicitly empty baseline.

## Control flow

Both public tests delegate to `testRedact`. The helper constructs the redactor, iterates over a curated sensitive-key list, and asserts each value is replaced with `"<redacted>"`. It then iterates over normal keys and asserts the original value is preserved.

## State and persistence behavior

The test is stateless apart from local lists and local `Configuration` instances. It does not persist configuration resources. The main behavior under test is pattern-driven, not value-driven.

## Dependencies and integration points

This file integrates with the default sensitive-key regex used by `ConfigRedactor` and by higher-level configuration dump paths such as `Configuration.dumpConfiguration` and `ConfServlet`. The key list covers S3A, Azure Blob/DFS, ADLS, WebHDFS OAuth, SSL keystores, HTTPFS SSL, and the sensitivity-regex configuration key itself.

## Risks and edge cases

- The test asserts a fixed redaction string; any intentional change to the public redaction marker requires coordinated updates.
- It covers representative key names, not every variant or case-normalization path.
- Because value content is irrelevant, secret-looking values under non-sensitive names are intentionally not redacted.
- False-positive coverage matters: server-side encryption algorithm and keystore location keys must remain visible, while actual key material and passwords must be hidden.

## Test signals

The main signals are two construction modes and paired positive/negative key sets. Additional useful tests would cover custom `hadoop.security.sensitive-config-keys` patterns, case sensitivity, regex metacharacter handling, and integration through servlet/configuration dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigRedactor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfiguration.java

## Purpose

`TestConfiguration` is the broad regression suite for Hadoop `Configuration`. It validates resource loading, XML parsing, final-parameter semantics, variable substitution, typed getters/setters, class loading, socket address utilities, storage/time parsing, dumping/redaction, property sources, tags, credential-provider password lookup, reload behavior, and concurrent access.

## Important APIs and types

- Resource loading: `addResource(InputStream)`, `addResource(Path)`, XInclude/fallback processing, relative include resolution, reload, cloning, and default-resource behavior.
- Property APIs: `set`, `get`, `getRaw`, `unset`, `clear`, `size`, `iterator`, `getProps`, `getPropertySources`, `getPropsWithPrefix`, `getValByRegex`, and `getFinalParameters`.
- Typed APIs: `getInt`, `getLong`, `getLongBytes`, `getBoolean`, `getFloat`, `getDouble`, `getClass`, `getClasses`, `getEnum`, `getPattern`, `getRange`, socket-address helpers, time duration helpers, and storage-size helpers.
- Serialization/dumping: `writeXml`, `writeXml(name, Writer)`, and `Configuration.dumpConfiguration`.
- Security integration: `ConfigRedactor` through dump tests and `CredentialProviderFactory`/`LocalJavaKeyStoreProvider` for `getPassword`.
- Support classes include `TestAppender`, JSON POJOs for dump validation, `Prop`, and a concurrency thread subclass.

## Control flow

Most tests synthesize temporary XML through helper methods such as `startConfig`, `appendProperty`, `appendCompactFormatProperty`, `appendPropertyByTag`, XInclude helpers, and entity declarations. `@BeforeEach` starts from `new Configuration(false)`; `@AfterEach` deletes the generated XML files.

Resource-loading tests cover input-stream closure, duplicate final warnings, final override warnings, compact property syntax, UTF-8/multibyte round trips, XML comments, escaped characters, CDATA, charset declarations, internal and system entities, XInclude with and without fallback, nested input-stream includes, relative includes, and duplicate-property ordering across included files. Reload tests mutate resource files, call `reloadConfiguration`, and verify overlay/programmatic values and final semantics.

Substitution tests use a Mockito spy to stub system properties and environment variables. They check normal substitution, public common-variable substitution, environment default forms (`-` and `:-`), restricted system-property mode, incomplete substitution strings, and self-referential substitutions that must remain literal.

Typed getter tests cover integer ranges, hex/integer/human-readable bytes, booleans, floats, doubles, classes, class arrays, mutable string collections, enums, time durations including precision warnings, storage units, regex patterns, socket addresses, and primitive setter/getter pairs. Dump tests parse JSON with Jackson and XML by reloading into `Configuration`, including single-property, all-property, non-existing-property, default-free configuration, source tracking, final tags, property expansion, and sensitive redaction. Later tests cover credential-provider password lookup through deprecated and new keys, prefix extraction, property tags, invalid tags, resource clone races, null-valued properties, and concurrent mutation/iteration.

## State and persistence behavior

The suite writes several temporary XML files in the working directory and deletes them in teardown. `Configuration` itself has layered state: loaded resources, overlay/programmatic properties, final parameters, property sources, deprecation metadata, class loader, restriction flags, tag maps, and optional null-value handling. Some tests intentionally mutate global/static state through deprecations, default resources, static DNS resolution, system property `file.encoding`, and log appenders; they attempt cleanup where practical.

Credential tests create a randomized local Java keystore, write password entries, flush the provider, and delete the temporary directory. Concurrency tests intentionally stress shared configuration maps by many writers and by iteration during mutation.

## Dependencies and integration points

The file integrates `Configuration` with filesystem `Path`/`FileUtil`, XML/XInclude parsing, Jackson JSON mapping, Log4j appenders, Mockito spies, AssertJ, Hadoop `NetUtils`, `CommonConfigurationKeysPublic`, credential-provider APIs, `SubjectInheritingThread`, platform-specific XML header handling, and Java time units. It is the main compatibility suite for configuration semantics consumed by nearly every Hadoop component.

## Risks and edge cases

- Many tests depend on global static configuration/deprecation state; ordering or parallel execution can expose leakage if names collide.
- XML parsing behavior is security-sensitive: entity and include support must remain constrained by Hadoop's secure XML utilities and expected resource resolution.
- Final-parameter handling is subtle when deprecated keys, resource order, programmatic overlays, reload, and empty/null values interact.
- Variable substitution can loop, partially parse, or unexpectedly expose environment/system properties; restricted mode is a security boundary.
- Dumping and servlet paths must consistently redact sensitive keys while preserving non-secret diagnostics.
- Concurrent mutation/iteration tests can be timing-sensitive and may miss rare races despite high iteration counts.

## Test signals

Strong signals include full XML round trips, direct parse of dump output, explicit exception assertions for malformed values, final override logging checks, credential-provider lookups, tag extraction, prefix extraction, reload mutation checks, and concurrency stress. Additional valuable coverage would include isolated global-state reset helpers, stronger XML hardening assertions, and targeted tests for deprecation leakage across test classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigurationDeprecation.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigurationDeprecation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigurationFieldsBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigurationFieldsBase.java

## Purpose

`TestConfigurationFieldsBase` is an abstract reusable JUnit base for checking that public configuration key constants in Java classes stay aligned with an XML defaults file. Subclasses provide the XML filename, configuration classes, skip lists, and strictness flags; the base extracts constants and XML properties, compares both directions, checks default-value consistency, and optionally detects default-port/value collisions.

## Important APIs and types

- Subclass hook: `initializeMemberVariables()`.
- Required fields: `xmlFilename` and `configurationClasses`.
- Strictness flags: `errorIfMissingConfigProps` and `errorIfMissingXmlProps`.
- Skip sets: exact and prefix skips for class constants and XML properties.
- Collision filters: `filtersForDefaultValueCollisionCheck`.
- Reflection helpers inspect public static final string fields and default-value fields named `DEFAULT_*`, `*_DEFAULT`, or derived from `*_KEY`.
- Test methods: `testCompareConfigurationClassAgainstXml`, `testCompareXmlAgainstConfigurationClass`, `testXmlAgainstDefaultValuesInConfigurationClass`, and `testDefaultValueCollision`.

## Control flow

`setupTestConfigurationFields` calls the subclass initializer, asserts required members, extracts valid config-property constants from every class, loads XML properties through a `Configuration(false)` with null-value support, extracts default-value constants, and computes two set differences.

Class-field extraction filters to public static final `String` fields, skips default-value fields, ignores partial prefixes/suffixes and XML filenames, applies explicit skip lists, and requires property-like values matching a dot-separated regex. XML extraction loads the defaults file through `Configuration`, iterates entries, respects skip lists, and preserves null-valued properties through `onlyKeyExists`.

The comparison tests log missing entries and assert only when the subclass enabled strict mode. The default-value test matches XML keys to constant names and then tries common default-constant naming conventions. The collision test filters default constants by configured substrings and asserts numeric defaults are unique within that filter.

## State and persistence behavior

The base caches extracted maps and missing-key sets as instance fields per test setup. It reads XML defaults through Hadoop `Configuration`; no new persistent files are written. Subclass-provided skip sets and flags are mutable instance state.

## Dependencies and integration points

The class depends on Java reflection, Hadoop test reflection utilities, Hadoop `Configuration`, JUnit 5, SLF4J logging, Apache Commons `StringUtils`, and subclass test suites for specific Hadoop modules. It integrates source constants with XML default configuration files.

## Risks and edge cases

- Regex-based property detection can skip valid nonstandard keys or accept constants that are not actual configuration keys.
- Reflection only sees declared fields on provided classes; inherited constants require explicit class inclusion if needed.
- Default-value matching relies on naming conventions, not semantic annotations.
- Tests may only log drift unless subclasses enable the strict error flags.
- `kvItr.remove()` during XML extraction assumes the configuration iterator supports removal safely.

## Test signals

This base produces useful drift signals: constants missing from XML, XML defaults missing from Java constants, XML/default constant mismatches, empty XML values, constants with no defaults, and duplicate numeric defaults under configured filters. Subclasses determine whether signals are advisory or failing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigurationFieldsBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigurationSubclass.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigurationSubclass.java

## Purpose

`TestConfigurationSubclass` verifies behavior expected by subclasses of `Configuration`: protected property access through `getProps`, reload callbacks through overridden `reloadConfiguration`, and non-quiet error reporting for missing resources.

## Important APIs and types

- `SubConf extends Configuration` exposes `getProperties()` by calling protected `getProps()`.
- `SubConf.reloadConfiguration()` calls `super.reloadConfiguration()` and records a `reloaded` flag.
- `Configuration.addDefaultResource` triggers reload behavior for existing configurations.
- `setQuietMode(false)` and `addResource("not-a-valid-resource")` exercise non-quiet failure when properties are loaded.

## Control flow

`testGetProps` constructs `SubConf(true)` and verifies default resources populate `hadoop.tmp.dir`. `testReload` constructs a subclass instance, adds `empty-configuration.xml` as a default resource, and expects the override to have been called. `testReloadNotQuiet` adds an invalid resource in non-quiet mode, verifies that adding alone does not reload, then calls `getProperties()` and expects a runtime failure containing `"not found"`.

## State and persistence behavior

The file uses a classpath XML resource and mutates global default resources through `Configuration.addDefaultResource`. `SubConf` keeps an in-memory boolean reload marker. No files are written.

## Dependencies and integration points

The tests integrate subclassing hooks in `Configuration` with the classpath resource `empty-configuration.xml`, default resource registration, protected property materialization, and quiet/non-quiet resource handling.

## Risks and edge cases

- Adding a default resource is global static state and can affect later configuration tests.
- The reload flag only proves the override was entered, not that all internal caches were refreshed correctly.
- Non-quiet failure is asserted via message substring, which can be brittle across exception wording changes.

## Test signals

Useful signals are subclass access to default-loaded properties, reload callback invocation after adding a default resource, lazy loading of invalid resources, and exception surfacing when quiet mode is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfigurationSubclass.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestDeprecatedKeys.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestDeprecatedKeys.java

## Purpose

`TestDeprecatedKeys` is a compact regression suite for deprecated configuration key compatibility. It validates a built-in deprecated key, XML write behavior after deprecation registration, and iteration/value propagation when one deprecated key maps to multiple replacement keys.

## Important APIs and types

- `Configuration.addDeprecation(String, String[])`.
- `Configuration.set`, `setBoolean`, `get`, `writeXml`, and `iterator`.
- `CommonConfigurationKeys.NET_TOPOLOGY_SCRIPT_FILE_NAME_KEY` as the replacement for `"topology.script.file.name"`.

## Control flow

`testDeprecatedKeys` sets the old topology script key and reads the modern common key. `testReadWriteWithDeprecatedKeys` sets an old key before registering deprecation, writes XML, and checks that both old and new names appear. `testIteratorWithDeprecatedKeysMappedToMultipleNewKeys` registers `"dK"` to `"nK1"` and `"nK2"`, repeatedly updates old and new names, checks alias values, and confirms iteration exposes all aliases plus a normal key.

## State and persistence behavior

The tests are in-memory and use a `ByteArrayOutputStream` for XML. Deprecation registration mutates global `Configuration` static state with simple test key names, so repeated execution depends on idempotent deprecation handling.

## Dependencies and integration points

This file overlaps with broader deprecation tests but covers specific public/common constants and XML serialization. It guards compatibility for users who still set legacy config keys.

## Risks and edge cases

- The test key names are very short and global; they can collide with other tests if deprecation state is not isolated.
- XML assertions are substring-based and do not validate structure or final/source metadata.
- Multi-new-key semantics are order-sensitive: later updates to one alias propagate to all aliases.

## Test signals

The file gives quick signals that old keys still read through new constants, deprecation registration after setting still affects XML output, and iterators include both deprecated and replacement keys with synchronized values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestDeprecatedKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestGetInstances.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestGetInstances.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestReconfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestReconfiguration.java

## Purpose

`TestReconfiguration` validates Hadoop's runtime reconfiguration framework. It covers property-difference detection, synchronous reconfiguration, visibility of configuration changes across threads, asynchronous reconfiguration task status, single-task enforcement, shutdown behavior, and correct updates/unsets of the parent cached configuration after successful reconfiguration.

## Important APIs and types

- `ReconfigurationUtil.getChangedProperties(Configuration newConf, Configuration oldConf)` returns `PropertyChange` records.
- `ReconfigurableBase` methods under test include `reconfigureProperty`, `startReconfigurationTask`, `getReconfigurationTaskStatus`, `shutdownReconfigurationTask`, `getConf`, `isPropertyReconfigurable`, and subclass hooks.
- Local `ReconfigurableDummy` implements synchronous behavior and `Runnable`.
- Local `AsyncReconfigurableDummy` blocks in `reconfigurePropertyImpl` with a latch to make running-task state observable.
- `ReconfigurationTaskStatus` exposes task start/end/stopped/hasTask state and per-property status.

## Control flow

`setUp` builds two configurations with one unchanged property, one changed property, one removed property, and one newly added property. `testGetChangedProperties` asserts all three change kinds are reported.

`testReconfigure` creates a dummy with three reconfigurable properties, verifies `isPropertyReconfigurable`, and exercises setting same value, null, changed value, unset-to-null, unset-to-value, and failures for non-reconfigurable properties. `testThread` runs a loop that watches a property until a synchronous reconfiguration changes it.

`testAsyncReconfigure` spies an async dummy to return synthetic changes, mark some properties reconfigurable, return success for one property, report non-reconfigurable for another, and throw for a third. It starts the background task, waits for stopped status, and inspects result messages. `testStartReconfigurationFailureDueToExistingRunningTask` holds the first task with a latch, verifies a second start fails, releases the task, starts a later task, then shuts down and verifies future starts fail. The final tests use `makeReconfigurable` to prove successful sync/async reconfiguration updates or unsets the stored `Configuration`.

## State and persistence behavior

State is held in `Configuration` objects owned by `ReconfigurableBase` and in background task status. No files are written. Asynchronous tests create background threads and must release latches/shutdown tasks to avoid lingering work.

## Dependencies and integration points

The suite integrates configuration comparison utilities, runtime reconfigurable services, `SubjectInheritingThread`, Hadoop `Time`, `GenericTestUtils.waitFor`, AssertJ, Mockito spies/stubs, latches, and optional status strings. It models behavior used by long-running Hadoop daemons that change selected configuration values without restart.

## Risks and edge cases

- Async task tests are timing-sensitive; helper polling must balance reliability and runtime.
- Property status maps omit successful changes without messages, so assertions must distinguish no-error optional from absent result.
- The parent configuration should only change after hook success; exception paths need careful coverage because partial changes could leave runtime state inconsistent.
- Starting after shutdown must fail deterministically to prevent task leaks.

## Test signals

Strong signals include change-kind detection, sync and async mutation/unset behavior, non-reconfigurable rejection, exception capture in task status, running-task exclusion, task timestamp ordering, shutdown rejection, and cross-thread visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestReconfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestStorageUnit.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestStorageUnit.java

## Purpose

`TestStorageUnit` validates the `StorageUnit` enum's binary storage conversions, unit metadata, default behavior, and rounding expectations across bytes, KB, MB, GB, TB, PB, and EB.

## Important APIs and types

- `StorageUnit.BYTES`, `KB`, `MB`, `GB`, `TB`, `PB`, and `EB`.
- Conversion methods: `toBytes`, `fromBytes`, `toKBs`, `toMBs`, `toGBs`, `toTBs`, `toPBs`, `toEBs`, and `getDefault`.
- Metadata methods: `getShortName`, `getSuffixChar`, `getLongName`, and `toString`.

## Control flow

The first six tests provide maps of input byte counts to expected conversions for byte-to-larger-unit conversions, including negative and zero values plus values that round to four decimal places. The remaining tests validate each unit's metadata, conversion to bytes, conversion from bytes, identity conversion, and conversion to other units using binary 1024 multipliers.

## State and persistence behavior

The test is stateless. Constants define binary unit magnitudes as doubles. No configuration or filesystem state is used.

## Dependencies and integration points

The file depends on AssertJ and the `StorageUnit` enum used by `Configuration.getStorageSize`/`setStorageSize`. It anchors expected display names and suffixes consumed by config parsing.

## Risks and edge cases

- Exact double equality is used for rounded results, so implementation changes to precision or rounding policy will break tests.
- The class spells terabyte conceptually as "Terra" in method name but expects `terabytes`; naming inconsistencies can confuse future maintainers.
- Extremely large EB/PB conversions approach precision limits of `double`; the tests explicitly note out-of-precision cases.

## Test signals

The suite provides complete unit coverage for metadata and representative positive, negative, zero, small, and large conversions. Complementary tests in `TestConfiguration` cover string parsing of storage-size configuration values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestStorageUnit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/empty-configuration.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/empty-configuration.xml

## Purpose

`empty-configuration.xml` is a minimal classpath configuration resource containing an empty `<configuration>` element. It supports tests that need a syntactically valid default resource without adding properties.

## Important APIs and types

- XML declaration and Apache license comment.
- Root `<configuration>` element with no `<property>` children.
- Loaded by `Configuration.addDefaultResource` in `TestConfigurationSubclass`.

## Control flow

There is no executable control flow. When added as a default resource, Hadoop `Configuration` parses it successfully and triggers normal resource/reload mechanics while contributing no key/value pairs.

## State and persistence behavior

The file is static test data stored in the source tree. It does not persist runtime state and intentionally leaves configuration property state unchanged.

## Dependencies and integration points

The resource integrates with `Configuration` classpath resource lookup and XML parser behavior. It is particularly useful for testing reload callbacks without changing defaults.

## Risks and edge cases

- If the resource is renamed or moved, tests using the absolute classpath path `/org/apache/hadoop/conf/empty-configuration.xml` will fail.
- Even an empty resource mutates global default-resource lists when registered through `addDefaultResource`.
- XML parser changes must continue to accept empty configurations.

## Test signals

The resource's signal is successful loading with no properties and normal reload behavior. Non-empty output from this resource would indicate accidental test fixture drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/empty-configuration.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/constants/ConfigConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/constants/ConfigConstants.java

## Purpose

`ConfigConstants` is a small final test-support constants holder for configuration keys used across Hadoop tests. It currently exposes the Avro serialization trusted-packages system property name.

## Important APIs and types

- `public final class ConfigConstants` with a private constructor to prevent instantiation.
- `CONFIG_AVRO_SERIALIZABLE_PACKAGES = "org.apache.avro.SERIALIZABLE_PACKAGES"`.

## Control flow

There is no runtime control flow beyond class loading. The private constructor enforces static-only usage.

## State and persistence behavior

The class contains a single immutable string constant and no mutable state or persistence behavior.

## Dependencies and integration points

The constant integrates tests with Avro's serialization package trust configuration. Keeping it centralized avoids string duplication across test code.

## Risks and edge cases

- The class is in test sources but documents an external dependency's system property; changes in Avro's property name would require coordinated updates.
- Because it is a constant, downstream references may inline the value at compile time.

## Test signals

The useful signal is compilation and use by tests that need to configure Avro trusted packages. There are no direct behavioral tests in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/constants/ConfigConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/constants/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/constants/package-info.java

## Purpose

`package-info.java` documents the `org.apache.hadoop.constants` test package as an evolving home for config constants used in Hadoop tests.

## Important APIs and types

- Package-level Javadoc.
- `package org.apache.hadoop.constants;`.

## Control flow

There is no executable control flow.

## State and persistence behavior

No state is stored. The file contributes package documentation only.

## Dependencies and integration points

It provides package metadata for the adjacent `ConfigConstants` class and any future test constants in the package.

## Risks and edge cases

- Documentation can drift if the package gains non-config constants or production-facing APIs.
- The package is under test sources, so its stated scope should remain test support.

## Test signals

The only signal is successful compilation and generated package documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/constants/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/CryptoStreamsTestBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/CryptoStreamsTestBase.java

## Purpose

`CryptoStreamsTestBase` is an abstract compliance suite for Hadoop crypto input/output streams. Concrete subclasses provide encrypted output and input streams; the base verifies that encryption/decryption preserves generated data across sequential reads, writes, IV offsets, sync operations, positioned reads, ByteBuffer reads, seek/skip/position behavior, enhanced ByteBuffer access, and unbuffering.

## Important APIs and types

- Abstract factories: `getOutputStream(int, byte[], byte[])` and `getInputStream(int, byte[], byte[])`.
- Shared crypto state: static `CryptoCodec codec`, fixed 16-byte key/IV, record count, and buffer sizes.
- Data generation: `RandomDatum.Generator` writes deterministic key/value pairs into `DataOutputBuffer`.
- Stream contracts under test: `Syncable`, `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `ByteBufferPositionedReadable`, `HasEnhancedByteBufferAccess`, and `CanUnbuffer`.
- Helper methods: `readAll`, `preadAll`, `byteBufferPreadAll`, `readCheck`, `positionedReadCheck`, `readFullyCheck`, `seekCheck`, `byteBufferReadCheck`, `byteBufferPreadCheck`, and `verify`.

## Control flow

`setUp` regenerates a random dataset for every test. `testRead` writes all data then reads it back with default and small buffers. `testWrite` writes with both buffer sizes and checks `FSDataOutputStream` position when applicable. `testCryptoIV` rewrites the counter portion of IVs with boundary values and verifies round trips.

`testSyncable` writes one third of the data, calls `hflush`, reads the visible prefix, writes the rest, calls `hsync`, and verifies full data. Positioned-read tests verify byte-array and ByteBuffer reads from fractional offsets without disturbing normal stream state. Read-fully tests verify exact data and EOF failures. Seek, get-position, available, and skip tests validate stateful stream positioning and error messages for invalid offsets. ByteBuffer tests cover heap/direct buffers and nonzero positions. `testCombinedOp` mixes sequential reads, seeks, skips, positioned reads, and ByteBuffer reads to validate position accounting. Enhanced ByteBuffer access uses a direct `ByteBufferPool`. `testUnbuffer` verifies buffered reads, positioned reads, and ByteBuffer positioned reads still work after unbuffering.

## State and persistence behavior

The base stores generated plaintext data in instance fields. Concrete subclasses decide where encrypted bytes are stored. Stream state under test includes crypto buffer positions, cipher counter alignment, underlying stream position, flushed visibility, and unbuffered buffer lifecycle. No files are written by the base itself.

## Dependencies and integration points

The class integrates crypto streams with Hadoop filesystem stream interfaces, random writable test data, direct buffer pools, `ReadOption.SKIP_CHECKSUMS`, `FSExceptionMessages`, AssertJ, JUnit timeouts, and `GenericTestUtils` exception checks. It is intended to be reused by multiple crypto stream implementations.

## Risks and edge cases

- Random seeds vary each run, increasing coverage but making failures less directly reproducible unless logs capture enough context.
- Tests assume 16-byte key/IV and counter semantics suitable for AES/CTR-like codecs.
- Positioned read helpers use accumulated total as the next position for some paths, so they mainly validate full sequential pread from zero rather than arbitrary sparse ranges.
- Enhanced ByteBuffer access requires correct buffer ownership/release behavior; the dummy pool does not validate returned buffers.
- Timeout values protect against hangs but may hide performance regressions until they cross a large threshold.

## Test signals

The base provides broad behavioral signals for crypto stream correctness: plaintext round trip, EOF handling, flush/sync visibility, IV counter boundaries, positioned-read consistency, direct/heap ByteBuffer correctness, seek/skip error handling, position accounting, enhanced buffer access, and unbuffer idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/CryptoStreamsTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoCodec.java

## Purpose

`TestCryptoCodec` validates Hadoop crypto codec implementations and interoperability. It tests JCE and OpenSSL AES/CTR codecs, JCE and OpenSSL SM4/CTR codecs where supported, encryption/decryption round trips, cross-codec interoperability, secure-random generation, byte-at-a-time reads, seeked decryption, and IV calculation correctness.

## Important APIs and types

- Codec classes: `JceAesCtrCryptoCodec`, `JceSm4CtrCryptoCodec`, `OpensslAesCtrCryptoCodec`, and `OpensslSm4CtrCryptoCodec`.
- Stream classes: `CryptoOutputStream` and `CryptoInputStream`.
- Configuration keys: cipher-suite key, SM4 codec-class key, and JCE provider key.
- Native/OpenSSL guards: `GenericTestUtils.assumeInNativeProfile`, `NativeCodeLoader.buildSupportsOpenssl`, `OpensslCipher.getLoadingFailureReason`, and `OpensslCipher.isSupported`.
- Test data and buffers: `RandomDatum`, `DataOutputBuffer`, `DataInputBuffer`, `SecureRandom`, and `TestCryptoStreams.FakeInputStream`.
- IV reference calculation uses `BigInteger` and Guava `Longs.toByteArray`.

## Control flow

Each codec test configures assumptions and provider settings, then calls `cryptoCodecTest` with an encryption codec class, a decryption codec class, a record count, and an IV. AES tests verify JCE-to-JCE, JCE-to-OpenSSL, OpenSSL-to-OpenSSL, and OpenSSL-to-JCE paths. SM4 tests set cipher suite/provider configuration and verify JCE/OpenSSL paths when supported. Overflow scenarios set the low eight IV bytes to `0xff` before round trips.

`cryptoCodecTest` reflectively constructs the encryption codec, generates `RandomDatum` records, encrypts them, reflectively constructs the decryption codec, decrypts through buffered `DataInputStream`, and compares every key/value pair plus hash-map lookup semantics. It then re-decrypts byte-by-byte and re-decrypts after seeking one third into the encrypted stream. Finally it calls `testSecureRandom`, which asks the codec for random byte arrays of several lengths and asserts two generated arrays differ.

`testCalculateIV` creates a JCE AES codec and compares `calculateIV(initIV, counter, IV)` against a `BigInteger` reference across overflow, sequential random IV/counter ranges, and random counter values.

## State and persistence behavior

Static `key` and `iv` byte arrays are regenerated before each test. `Configuration conf`, record count, and random seed are instance state. Data is held in memory buffers. Native/OpenSSL availability affects whether tests execute or are skipped.

## Dependencies and integration points

The file integrates codec class loading through Hadoop `ReflectionUtils`, crypto stream read/write paths, OpenSSL native support, BouncyCastle for SM4 JCE provider selection, Hadoop random writable data, and the fake seekable input stream from `TestCryptoStreams`.

## Risks and edge cases

- Native-profile and OpenSSL assumptions mean important interoperability paths may be skipped in non-native test profiles.
- Secure-random tests only assert non-equality between two arrays; they do not provide statistical quality guarantees.
- `testCalculateIV` is expensive because it runs many counters across many random IVs; timeout protects hangs but not necessarily performance drift.
- Cross-codec tests rely on class names as strings; renames or provider changes require test updates.
- Static mutable key/IV arrays are shared within the test class and must be reset before each test.

## Test signals

Strong signals include full record round trips, zero-record behavior, cross-provider interoperability, counter overflow IV handling, byte-at-a-time decryption, seeked decryption, secure-random output shape/non-repeat, and independent IV arithmetic validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoOutputStreamClosing.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoOutputStreamClosing.java

## Purpose

`TestCryptoOutputStreamClosing` verifies whether `CryptoOutputStream` closes its wrapped `OutputStream` according to the constructor's close-underlying-stream flag, including the failure path where flushing during close throws.

## Important APIs and types

- `CryptoCodec.getInstance(new Configuration())` initializes a codec once for all tests.
- `CryptoOutputStream(OutputStream, CryptoCodec, byte[] key, byte[] iv, long streamOffset, boolean closeOutputStream)` is the constructor under test.
- Mockito mocks/spies verify wrapped stream `close()` calls and inject `flush()` failure.
- `LambdaTestUtils.intercept` asserts the expected `IOException`.

## Control flow

`testOutputStreamClosing` constructs a crypto stream with `closeOutputStream=true`, closes it, and verifies the wrapped stream is closed. `testOutputStreamNotClosing` repeats with `false` and verifies no wrapped close. `testUnderlyingOutputStreamClosedWhenExceptionClosing` spies the crypto stream so `flush()` throws during close, intercepts the exception, and verifies the wrapped stream is still closed in the cleanup path.

## State and persistence behavior

State is in mocked streams and one static codec. No bytes are written and no files are persisted. The key and IV arrays are zero-filled test arrays.

## Dependencies and integration points

The test integrates `CryptoOutputStream` close semantics with generic Java `OutputStream`, Hadoop `CryptoCodec`, Mockito, and Hadoop's lambda exception helper. Correct behavior matters for filesystem streams because closing or preserving the wrapped stream is caller-controlled.

## Risks and edge cases

- The tests do not verify idempotent double-close behavior or whether exceptions from the wrapped stream close are suppressed or propagated correctly.
- The flush failure is injected by spying on `CryptoOutputStream`, not by a real codec/output failure.
- No encrypted data is written, so buffer-finalization behavior during close is not covered here.

## Test signals

The key signals are positive close propagation, negative close suppression, and close propagation despite an earlier close-time flush exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoOutputStreamClosing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreams.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreams.java

## Purpose

`TestCryptoStreams` is the concrete in-memory implementation of `CryptoStreamsTestBase` for Hadoop `CryptoInputStream` and `CryptoOutputStream`. It supplies fake underlying streams implementing Hadoop filesystem stream interfaces and adds capability-advertising tests.

## Important APIs and types

- `getOutputStream` wraps a `DataOutputBuffer` in `FakeOutputStream`, then in `CryptoOutputStream`.
- `getInputStream` wraps stored encrypted bytes in `DataInputBuffer`, then `FakeInputStream`, then `CryptoInputStream`.
- `FakeOutputStream` implements `OutputStream`, `Syncable`, `CanSetDropBehind`, and `StreamCapabilities`.
- `FakeInputStream` implements `InputStream`, `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `ByteBufferPositionedReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `CanUnbuffer`, and `StreamCapabilities`.
- `testHasCapability` uses `ContractTestUtils.assertCapabilities`.

## Control flow

`init` creates the default `CryptoCodec`. Output creation uses an anonymous `DataOutputBuffer` whose `flush` and `close` snapshot the backing encrypted byte array and length. `FakeOutputStream` validates write arguments, rejects writes after close, forwards bytes to the buffer, implements `hflush`/`hsync` as flushes, and advertises `hflush`, `hsync`, and `dropbehind`.

`FakeInputStream` stores a byte array and cursor. It implements sequential reads, ByteBuffer reads, `available`, `skip`, `seek`, `seekToNewSource`, positioned byte-array and ByteBuffer reads, `readFully` variants with EOF checks, enhanced ByteBuffer reads via a supplied pool, no-op release/readahead/dropbehind/unbuffer, and capability advertising for readahead/dropbehind/unbuffer/ByteBuffer read/pread. Boundary checks reject negative positions and reads/seeks beyond EOF.

Inherited tests from `CryptoStreamsTestBase` run against these fake streams. `testHasCapability` specifically verifies that crypto wrappers delegate or expose the expected stream capabilities from the underlying fake streams.

## State and persistence behavior

The concrete test stores encrypted output in instance fields `buf` and `bufLen`. Fake streams maintain in-memory cursor and closed flags. No filesystem persistence occurs.

## Dependencies and integration points

This file integrates crypto streams with many Hadoop stream capability interfaces. The fake streams are also reused by `TestCryptoCodec` for seeked decryption. Capability behavior connects to Hadoop filesystem contract testing.

## Risks and edge cases

- Fake streams model Hadoop stream interfaces but are not full filesystem streams; real filesystem buffering, checksums, descriptors, and resource ownership may differ.
- `FakeInputStream.getFileDescriptor` returns null while advertising `HasFileDescriptor`; consumers must tolerate that in tests.
- Enhanced ByteBuffer read obtains direct buffers but `releaseBuffer` is a no-op, so pool lifecycle bugs are not caught.
- `hasCapability` lowercases input without a null guard; null capability behavior is not covered.
- `FakeOutputStream.close` snapshots data and marks closed but does not check close errors from an external resource.

## Test signals

The inherited suite verifies data correctness, positioning, ByteBuffer operations, sync, unbuffer, and IV behavior. This class adds concrete capability checks for crypto wrappers, ensuring expected capability pass-through for input and output streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreams.java -->
