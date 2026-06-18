# Research: subset-b-007992

Grouped research for the Ozone HDDS config and container-service files in this work item. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/util/NativeCRC32Wrapper.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/util/NativeCRC32Wrapper.java

## Purpose
Test-scope adapter that exposes Hadoop common's package-private `NativeCrc32` to Ozone benchmarks so native CRC32 and CRC32C implementations can be compared with Ozone checksum code.

## Important APIs, Types, And Functions
Constants `CHECKSUM_CRC32` and `CHECKSUM_CRC32C`, availability check `isAvailable()`, ByteBuffer and byte-array verification helpers, and ByteBuffer and byte-array calculation helpers. All public methods are thin static delegates.

## Control Flow
Callers check native-library availability, then pass checksum buffers, data buffers, offsets, lengths, file name, and base position through unchanged to `NativeCrc32`. Verification may throw `ChecksumException`; calculation mutates the supplied sums buffer or array.

## State And Persistence
The wrapper has no persistent state and cannot be instantiated. State is entirely in caller-owned buffers and Hadoop native CRC library availability.

## Dependencies And Integration Points
Integrates with Hadoop `org.apache.hadoop.util.NativeCrc32`, `java.nio.ByteBuffer`, and Hadoop `ChecksumException`. It exists in the same package to cross the package-private boundary.

## Risks
Because this is only a wrapper, risks are API drift in Hadoop's package-private class, incorrect buffer positions/offsets supplied by benchmarks, and accidentally depending on this test helper from production code.

## Test Signals
Benchmark and test signals are native CRC availability detection, matching CRC32/CRC32C results for ByteBuffer and byte-array paths, and expected `ChecksumException` behavior for corrupted data.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/util/NativeCRC32Wrapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/config/pom.xml

## Purpose
Maven module descriptor for `hdds-config`, the lightweight jar containing Ozone configuration annotations, reflection utilities, parsers, and the annotation processor.

## Important APIs, Types, And Functions
Declares parent `hdds`, artifact `hdds-config`, jar packaging, dependencies on `hadoop-common` with broad exclusions and `slf4j-api`, plus test Guava. Build plugins configure compiler and test jar generation.

## Control Flow
Main compile disables annotation processing with `<proc>none>` so the module can compile its own processor without recursive execution. Test compile enables `ConfigFileGenerator` from the built `hdds-config` artifact and passes an empty `artifactId` processor option.

## State And Persistence
No runtime state. Build outputs include the main jar, test jar, and generated test compile resources such as `ozone-default-generated.xml`.

## Dependencies And Integration Points
Feeds every module that uses `@Config` and the annotation processor. The test jar exposes test configuration examples to downstream tests.

## Risks
The broad Hadoop dependency exclusion keeps the module small but can hide transitive assumptions. Processor configuration must remain synchronized with `ConfigFileGenerator` options and artifact version properties.

## Test Signals
Signals include `mvn -pl hadoop-hdds/config test`, generated default XML during test compile, and consumers resolving both main and test jars without unexpected transitive dependency expansion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/Config.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/Config.java

## Purpose
Runtime-retained field annotation marking a Java field as backed by an Ozone/Hadoop configuration property.

## Important APIs, Types, And Functions
Annotation members define the property `key`, `defaultValue`, human `description`, `ConfigType`, time and storage units, `ConfigTag[]`, and a `reconfigurable` flag.

## Control Flow
Reflection utilities scan fields with this annotation, choose explicit or auto-detected type conversion, read values from a `ConfigurationSource`, and write back through a `ConfigurationTarget`. The annotation processor also reads it when generating XML fragments.

## State And Persistence
The annotation has no runtime state, but its metadata is persisted into generated configuration XML and drives in-memory object injection.

## Dependencies And Integration Points
Integrated with `ConfigGroup`, `ConfigType`, `ConfigTag`, `ConfigurationReflectionUtil`, and `ConfigFileGenerator`.

## Risks
Misdeclared keys, defaults, or units can produce wrong runtime values. `reconfigurable=true` on final fields is rejected later by reflection checks, not by the annotation itself.

## Test Signals
Tests should cover injection for each supported type, generated XML entries, prefix validation through `ConfigGroup`, and reconfiguration only for fields with the flag set.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/Config.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigFileAppender.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigFileAppender.java

## Purpose
DOM-based writer for Ozone generated/default XML configuration fragments.

## Important APIs, Types, And Functions
Constructor creates secure XML builder. Public methods are `init()`, `load(InputStream)`, `addConfig(key, defaultValue, description, tags)`, and `write(Writer)`. Private `addXmlElement` appends text nodes.

## Control Flow
A caller initializes or loads a `<configuration>` document, appends `<property>` nodes containing name, value, description, and comma-separated tag values, then serializes with UTF-8 and indentation through a secure transformer.

## State And Persistence
Holds a mutable DOM `Document` and a `DocumentBuilder`. Persisted state is the XML written to the caller's writer or resource.

## Dependencies And Integration Points
Used by `ConfigFileGenerator`; depends on Hadoop `XMLUtils` secure XML factories and W3C DOM APIs.

## Risks
`document` must be initialized or loaded before `addConfig`. Existing resource loading and writing rely on DOM memory, so very large generated files could be costly. Text nodes correctly avoid XML injection, but bad descriptions still appear verbatim.

## Test Signals
Tests should assert empty configuration creation, appending property fields, tag formatting, secure parse/write behavior, and round-tripping existing XML resources.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigFileAppender.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigFileGenerator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigFileGenerator.java

## Purpose
Annotation processor that generates Ozone default configuration XML fragments from classes annotated with `@ConfigGroup` and fields annotated with `@Config`.

## Important APIs, Types, And Functions
Processor metadata includes `@SupportedAnnotationTypes(ConfigGroup)`, `@SupportedOptions("artifactId")`, and Java 8 source support. Core methods are `process()` and `writeConfigAnnotations()`.

## Control Flow
Each annotation-processing round skips final processing, chooses `ozone-default-generated.xml` or `<artifactId>-default.xml`, attempts to load an existing class-output resource, scans grouped config classes, validates each field key starts with the group prefix plus dot, appends each config entry, and writes only when the resource did not previously exist.

## State And Persistence
The processor persists generated XML into compiler class output. It keeps no cross-round state beyond local DOM state inside `ConfigFileAppender`.

## Dependencies And Integration Points
Integrated with Maven compiler plugin configuration, `ConfigGroup`, `Config`, `ConfigTag`, and Java annotation processing `Filer` APIs.

## Risks
If a resource already exists, this implementation loads and mutates it but does not rewrite it, so later rounds or repeated processing may not persist additional entries. Prefix validation reports compiler errors but processing continues. Build behavior depends on `artifactId` option consistency.

## Test Signals
Signals include compile-time generated XML content, prefix mismatch diagnostics, tests around `ConfigurationExample`, and module builds that enable this processor in downstream modules.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigFileGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigGroup.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigGroup.java

## Purpose
Runtime-retained type annotation that declares the common prefix for a configuration POJO.

## Important APIs, Types, And Functions
Single API member `prefix()` returns the expected prefix for `@Config.key()` values within the annotated class.

## Control Flow
The annotation processor finds classes with `@ConfigGroup`, then validates and writes enclosed `@Config` fields. Runtime code can use the annotation as descriptive metadata, though injection uses full keys from fields.

## State And Persistence
No mutable state; the prefix becomes part of compile-time validation and generated XML semantics.

## Dependencies And Integration Points
Integrated with `ConfigFileGenerator` and classes such as `ConfigurationExample` or production config POJOs.

## Risks
Prefix drift between class-level `ConfigGroup` and field-level full keys breaks generated config validation. The annotation does not enforce the prefix at runtime.

## Test Signals
Tests should include matching and non-matching prefixes and properties whose suffix itself contains the prefix-like text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigTag.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigTag.java

## Purpose
Central enum of system-supported configuration tags used to categorize Ozone configuration properties.

## Important APIs, Types, And Functions
Values cover security, storage, SCM, OM, datanode, Ratis, performance, management, crypto compliance, disk balancer, and related domains. `Enum.name()` is used when writing XML tags.

## Control Flow
`Config` annotations attach one or more tags to a field. `ConfigFileAppender` joins the enum names into the generated `<tag>` element.

## State And Persistence
Enum constants are static metadata only; generated XML persists their names as strings.

## Dependencies And Integration Points
Integrated with config annotations, generated default XML, and downstream documentation or filtering tools consuming Ozone config tags.

## Risks
Renaming or removing a tag changes generated XML and can break external documentation/filtering. Empty tag arrays are allowed and produce an empty tag element.

## Test Signals
Signals include generated XML tag content, config-doc tooling behavior, and compile failures for annotations using removed enum constants.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigTag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigType.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigType.java

## Purpose
Enum implementing parsing and write-back behavior for supported configuration field types.

## Important APIs, Types, And Functions
Types include `AUTO`, `STRING`, `BOOLEAN`, `INT`, `LONG`, `TIME`, `SIZE`, `CLASS`, `DOUBLE`, and `FLOAT`. Each concrete type implements `parse()` and `set()` against `ConfigurationTarget`.

## Control Flow
Injection detects `AUTO` from field type, parses source strings into Java values, and assigns fields. Write-back converts Java values to configuration strings through target setters. Time supports `Duration` and long durations; size parses `StorageSize` and rounds bytes.

## State And Persistence
No persistent state. It is a stateless conversion table, but write-back mutates the supplied `ConfigurationTarget`.

## Dependencies And Integration Points
Depends on `TimeDurationUtil`, `StorageSize`, `StorageUnit`, `ConfigurationTarget`, and Java `Duration`/`TimeUnit`/`Class` loading.

## Risks
Type mismatch causes runtime `ConfigurationException`. `SIZE` narrows to `int` without range checking beyond Java cast. `CLASS` loads by class name and can fail late. `AUTO` intentionally throws if used directly.

## Test Signals
Tests should exercise every parse/set branch, `Duration` nanosecond versus millisecond write-back, size unit conversion, unsupported field types, class loading, and invalid numeric strings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationException.java

## Purpose
Unchecked exception used for configuration injection, parsing, XML generation, and write-back failures.

## Important APIs, Types, And Functions
Provides no-arg, message, and message-plus-cause constructors.

## Control Flow
Callers wrap checked reflection, XML, parsing, or IO-related failures in this runtime exception to avoid polluting configuration APIs with checked exceptions.

## State And Persistence
No state beyond standard `RuntimeException` message and cause fields.

## Dependencies And Integration Points
Used throughout `org.apache.hadoop.hdds.conf`, especially reflection utilities and XML appender/generator code.

## Risks
Because it is unchecked, failures can surface at service startup or reconfiguration time unless callers validate config early. Some constructors allow empty messages, reducing diagnostic value.

## Test Signals
Signals include negative tests for malformed values, unsupported types, final annotated fields, bad XML resources, and post-construct rollback failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationReflectionUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationReflectionUtil.java

## Purpose
Reflection engine for injecting configuration values into annotated POJOs, extracting metadata, updating targets from objects, and applying dynamic reconfiguration.

## Important APIs, Types, And Functions
Important APIs include `injectConfiguration`, `reconfigureProperty`, `mapReconfigurableProperties`, `updateConfiguration`, `getDefaultValue`, `getKey`, `getType`, and package-visible `callPostConstruct`. Helpers force private field access and reject final fields.

## Control Flow
Injection scans declared fields, skips non-reconfigurable fields during reconfiguration, reads source values with defaults, detects type when needed, parses through `ConfigType`, and force-sets fields. Single-property reconfiguration stores the old value, sets the new value, invokes `@PostConstruct`, and rolls back on post-construct failure.

## State And Persistence
State lives in target config objects. The utility mutates private fields and target configuration stores, but it persists nothing itself.

## Dependencies And Integration Points
Depends on `Config`, `ConfigType`, `ConfigurationSource`, `ConfigurationTarget`, `PostConstruct`, reflection APIs, and `Duration` detection.

## Risks
It scans only declared fields for injection and reconfigurable mapping, while metadata lookup walks superclasses. `Class.newInstance` callers require no-arg constructors. Access toggling can interact with newer Java access restrictions. Post-construct rollback covers the changed field but not other side effects.

## Test Signals
Tests should cover private fields, final-field rejection, reconfigurable filtering, post-construct invocation and rollback, superclass metadata lookup, null value write-back skipping, and all auto-detected types.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationReflectionUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationSource.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationSource.java

## Purpose
Read-only abstraction over configuration providers with default helpers for typed values, prefix maps, object injection, class loading, durations, storage sizes, and enums.

## Important APIs, Types, And Functions
Required methods are `get`, `getConfigKeys`, and `getPassword`. Defaults include numeric/boolean getters, trimmed string splitting, prefix matching, `getObject`, `reconfigure`, `getClass`, `getClasses`, `getTimeDuration`, `getBufferSize`, `getStorageSize`, and `getEnum`.

## Control Flow
Consumers read raw strings and default helpers parse them. `getObject` instantiates a no-arg POJO, injects fields through `ConfigurationReflectionUtil`, and calls `@PostConstruct`. Prefix helpers scan all keys and either preserve or trim the matched prefix.

## State And Persistence
No internal persistence; state is owned by implementing classes. Object injection mutates newly created or supplied objects.

## Dependencies And Integration Points
Implemented by mutable/test sources and Ozone configuration classes. Depends on `TimeDurationUtil`, `StorageSize`, `StorageUnit`, and reflection utilities.

## Risks
`getTrimmedStringsFromValue` returns one empty string for a blank non-null value. `getClass(String, Class<?>)` appears to call `Class.forName(name)` instead of the configured value string, which would load the property key rather than the class value. Numeric parsing is eager and unchecked.

## Test Signals
Tests should cover prefix matching, blank/trimmed lists, object injection, reconfiguration filtering, storage and time parsing, class/class-array loading, and the suspected `getClass` value bug.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationTarget.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationTarget.java

## Purpose
Write abstraction for configuration stores with typed default setters.

## Important APIs, Types, And Functions
Requires `set(String, String)`. Defaults write ints, longs, doubles, floats, booleans, time durations, storage sizes, string arrays, classes, and enums as strings.

## Control Flow
Reflection write-back calls `ConfigType.set`, which delegates to these typed setters. Time duration and storage setters preserve the annotation's unit in string form through utility formatting.

## State And Persistence
State is persisted only by implementers; this interface just normalizes conversion to string values.

## Dependencies And Integration Points
Used by `MutableConfigurationSource` and concrete Ozone configuration implementations. Depends on `TimeDurationUtil.ParsedTimeDuration`, `StorageUnit`, and Java `TimeUnit`.

## Risks
String formatting compatibility matters because generated values may later be parsed by `ConfigurationSource`. Unit suffix mapping must stay in sync with the parser.

## Test Signals
Tests should round-trip values through a mutable implementation for all primitive, time, storage, class, enum, and string-array setter paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ConfigurationTarget.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/MutableConfigurationSource.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/MutableConfigurationSource.java

## Purpose
Combines read-only and write-only configuration contracts for mutable configuration providers.

## Important APIs, Types, And Functions
Extends `ConfigurationSource` and `ConfigurationTarget` without adding methods.

## Control Flow
Implementations can both provide source values for object injection and accept write-back from config POJOs via `setFromObject` on concrete classes or `ConfigurationReflectionUtil.updateConfiguration`.

## State And Persistence
All state is implementation-owned; the interface itself has no fields.

## Dependencies And Integration Points
Used by test in-memory configuration and production mutable configuration classes such as Ozone configuration wrappers.

## Risks
Because no additional contract is enforced, implementers must keep read and write views consistent and handle null/password behavior explicitly.

## Test Signals
Signals include round-trip tests that inject an object from a mutable source, mutate object fields, write back, and read the same keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/MutableConfigurationSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/PostConstruct.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/PostConstruct.java

## Purpose
Runtime-retained method annotation for hooks that should run after configuration object injection.

## Important APIs, Types, And Functions
No members. It targets methods and is discovered by `ConfigurationReflectionUtil.callPostConstruct` through public `getMethods()`.

## Control Flow
After full object creation or during single-property reconfiguration, reflection invokes every public method annotated with `@PostConstruct`. Reconfiguration rolls back the changed field if a post-construct hook fails.

## State And Persistence
The annotation itself has no state. Hook methods may mutate object state or external state.

## Dependencies And Integration Points
Integrated with `ConfigurationSource.getObject` and `ConfigurationReflectionUtil.reconfigureProperty`.

## Risks
Only public inherited methods are scanned. Hooks with side effects are not fully rolled back except for the reconfigured field. Checked exceptions are wrapped.

## Test Signals
Tests should cover hook execution after injection, runtime exception propagation, rollback on reconfiguration failure, and behavior for non-public annotated methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/PostConstruct.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurableConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurableConfig.java

## Purpose
Base class for annotated configuration POJOs that expose dynamic reconfiguration metadata and single-property updates.

## Important APIs, Types, And Functions
Public APIs are `reconfigurableProperties()` and `reconfigureProperty(String key, String value)`. It caches no explicit fields.

## Control Flow
`reconfigurableProperties` asks `ConfigurationReflectionUtil` for annotated fields marked reconfigurable. `reconfigureProperty` looks up the field by key and applies the new string value through reflection; unknown keys fail with `ConfigurationException`.

## State And Persistence
State is in subclass fields. Reconfiguration mutates those fields and invokes post-construct hooks as needed.

## Dependencies And Integration Points
Used by `ConfigurationExample` and production config classes that need runtime reconfiguration through `ReconfigurationHandler`.

## Risks
The property map is rebuilt on each call and only declared fields are considered. Misdeclared reconfigurable fields fail at runtime. Single-property updates depend on string parsing and field rollback semantics.

## Test Signals
Tests should verify listed keys, successful dynamic property changes, rejection of non-reconfigurable or unknown keys, and post-construct rollback behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurableConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/StorageSize.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/StorageSize.java

## Purpose
Small value object representing a numeric storage size and its parsed `StorageUnit`.

## Important APIs, Types, And Functions
APIs include constructor, `parse(String)`, `parse(String, StorageUnit defaultUnit)`, `getUnit`, `getValue`, and `toString`. Parsing accepts long names, short names, and single-letter suffixes.

## Control Flow
Parsing trims and lowercases input, finds the first matching unit in `StorageUnit.values()` order, strips the longest matched suffix, parses the numeric part as double, and optionally falls back to a default unit when no suffix is found.

## State And Persistence
Instances are immutable with final unit and value fields. No persistence beyond string/XML configuration values.

## Dependencies And Integration Points
Used by `ConfigurationSource.getStorageSize` and `ConfigType.SIZE`; depends on `StorageUnit` conversion methods.

## Risks
Unit matching relies on enum order, especially bytes being last because suffix `b` overlaps other units. Values are doubles, so precision and later rounding/casting matter. Blank values throw `IllegalStateException`, while malformed values throw `IllegalArgumentException`.

## Test Signals
Tests should cover every suffix form, default-unit parsing, decimals, case/whitespace, invalid and blank strings, and overlap cases like `1mb` versus `1b`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/StorageSize.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/StorageUnit.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/StorageUnit.java

## Purpose
Enum defining binary storage units from bytes through exabytes and conversion helpers among them.

## Important APIs, Types, And Functions
Each unit implements conversion methods `toBytes`, `toKBs`, `toMBs`, `toGBs`, `toTBs`, `toPBs`, `toEBs`, `fromBytes`, suffix accessors, `getDefault`, and `toString`. Helpers use `BigDecimal` with scale 4.

## Control Flow
Converters multiply or divide by powers of 1024. `StorageSize.parse` iterates units in declared order, relying on `BYTES` being last so the `b` suffix does not preempt longer suffixes.

## State And Persistence
No mutable state; constants encode unit metadata and conversion ratios.

## Dependencies And Integration Points
Used by `Config`, `ConfigType.SIZE`, `ConfigurationSource`, `ConfigurationTarget`, and `StorageSize`.

## Risks
Double output plus 4-decimal rounding can lose precision for very large values. Comments mention overflow behavior but `BigDecimal.doubleValue()` may still produce infinity for enormous values. Enum order is a correctness contract.

## Test Signals
Tests should cover conversion matrix, suffix names, byte overlap ordering, large values, fractional values, and round-trip parse/format with `StorageSize`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/StorageUnit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/TimeDurationUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/TimeDurationUtil.java

## Purpose
Utility for parsing string time durations with suffixes and converting them to `Duration` or long values in caller-requested units.

## Important APIs, Types, And Functions
Public APIs are `getTimeDurationHelper(name, value, unit)` and `getDuration(name, value, unit)`. Inner enum `ParsedTimeDuration` maps ns, us, ms, s, m, h, and d suffixes to `TimeUnit` and `ChronoUnit`.

## Control Flow
Parsing trims/lowercases the input, detects the suffix by enum order, strips it, parses the numeric portion as a long, and builds a `Duration`. If no suffix is present, it logs a warning and uses the provided default unit.

## State And Persistence
No persistent state beyond logger. Returned values are derived from strings.

## Dependencies And Integration Points
Used by `ConfigurationSource`, `ConfigurationTarget`, and `ConfigType.TIME`.

## Risks
`getTimeDurationHelper` converts through milliseconds, so sub-millisecond durations can be truncated when returning long values. Negative values are not rejected. Blank or non-numeric strings fail at parse time.

## Test Signals
Tests should cover all suffixes, no-suffix default unit behavior, uppercase input, sub-millisecond truncation, negative durations, and invalid strings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/TimeDurationUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/package-info.java

## Purpose
Package documentation for generic Ozone configuration annotations, tools, and generators.

## Important APIs, Types, And Functions
No APIs beyond the `org.apache.hadoop.hdds.conf` package declaration and Javadoc.

## Control Flow
The file is consumed by Javadoc and package-level documentation generation only.

## State And Persistence
No runtime state or persistence.

## Dependencies And Integration Points
Documents the package containing annotations, reflection utilities, source/target contracts, parsers, and annotation processor.

## Risks
Risk is documentation drift if package responsibilities change without updating the summary.

## Test Signals
Signals are generated Javadoc/package docs and package-level checkstyle/license validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/main/java/org/apache/hadoop/hdds/conf/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/ConfigurationExample.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/ConfigurationExample.java

## Purpose
Test fixture configuration POJO that exercises string, boolean, int, long time, `Duration`, size, double, reconfigurable, and prefix-containing config keys.

## Important APIs, Types, And Functions
Class is annotated `@ConfigGroup(prefix="ozone.test.config")` and extends `ReconfigurableConfig`. Fields use `@Config` with defaults, types, units, tags, and one `reconfigurable=true` property. Getters and selected setters expose test assertions.

## Control Flow
Tests create it through `ConfigurationSource.getObject`, causing reflection injection from defaults or in-memory overrides. Reconfiguration tests update only the dynamic field while non-reconfigurable fields remain unchanged.

## State And Persistence
State is private fields populated by injection. No external persistence except when written back through mutable configuration.

## Dependencies And Integration Points
Used by tests for reflection utility, configuration source, reconfiguration, and generated XML.

## Risks
As a test fixture, it must remain broad enough to cover supported types. Adding fields with invalid prefixes or defaults can break annotation-processor tests.

## Test Signals
Signals include injected default values, override values, generated XML entries, dynamic property listing, reconfiguration behavior, and set-from-object round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/ConfigurationExample.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/InMemoryConfigurationForTesting.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/InMemoryConfigurationForTesting.java

## Purpose
Simple mutable map-backed configuration source used by unit tests.

## Important APIs, Types, And Functions
Implements `MutableConfigurationSource` with `get`, `getConfigKeys`, `getPassword`, and `set`. Constructors create an empty map or one initial key/value.

## Control Flow
Tests set raw strings, then use default interface methods for typed reads, object injection, prefix scans, and write-back. Password reads return the stored string as a char array.

## State And Persistence
State is a `HashMap<String,String>` owned by the test instance; it is not synchronized or persisted.

## Dependencies And Integration Points
Used by config unit tests and examples. Relies heavily on default methods from `ConfigurationSource` and `ConfigurationTarget`.

## Risks
`getPassword` will throw `NullPointerException` for missing keys. The map is mutable and unsynchronized, so it is not suitable for concurrent tests without wrapping.

## Test Signals
Signals include prefix matching, typed setter/getter round trips, object injection from defaults and overrides, and password behavior for present keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/InMemoryConfigurationForTesting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigFileAppender.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigFileAppender.java

## Purpose
Unit test for generated configuration XML appending.

## Important APIs, Types, And Functions
Uses AssertJ assertions, `ConfigFileAppender`, `StringWriter`, and `ConfigTag` values.

## Control Flow
The test initializes an appender, adds one config property with key/default/description/tags, writes XML to a string, and asserts the output contains expected property fields.

## State And Persistence
No persistent state beyond in-memory writer output.

## Dependencies And Integration Points
Validates `ConfigFileAppender` behavior independent of annotation processing.

## Risks
The test is content-substring based, so it may miss XML structure issues or ordering changes outside the asserted fields.

## Test Signals
Signals are successful XML creation, tag joining, text value preservation, and no exceptions during secure transformer writing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigFileAppender.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigFileGenerator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigFileGenerator.java

## Purpose
Unit/integration test for annotation processor output generated during test compilation.

## Important APIs, Types, And Functions
Uses classloader resource lookup for `ozone-default-generated.xml` and AssertJ/JUnit assertions.

## Control Flow
Because the Maven test compile enables `ConfigFileGenerator`, the test opens the generated resource and asserts it contains expected entries from `ConfigurationExample`.

## State And Persistence
State is the generated class-output XML file produced by the compiler.

## Dependencies And Integration Points
Validates the Maven compiler processor setup, `ConfigFileGenerator`, and `ConfigurationExample` annotations together.

## Risks
If processor output is stale or not rewritten across rounds, this test can pass while missing newly added entries unless assertions are expanded.

## Test Signals
Signals include presence of `ozone-default-generated.xml`, expected keys/defaults/descriptions/tags, and processor execution during test compile.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigFileGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigurationReflectionUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigurationReflectionUtil.java

## Purpose
Tests metadata lookup and reconfigurable-property discovery in `ConfigurationReflectionUtil`.

## Important APIs, Types, And Functions
Parameterized data covers field names mapped to expected `ConfigType`, key, and default value. A separate test checks `mapReconfigurableProperties` returns only the dynamic config key.

## Control Flow
The test invokes `getType`, `getKey`, `getDefaultValue`, and `mapReconfigurableProperties` against `ConfigurationExample`, non-config classes, and missing fields.

## State And Persistence
No persistent state; all checks are in-memory reflection assertions.

## Dependencies And Integration Points
Covers reflection metadata APIs used by documentation, reconfiguration, and tests.

## Risks
Coverage does not directly test injection failure paths, post-construct behavior, or final field rejection.

## Test Signals
Signals include expected optionals for annotated fields, empty optionals for missing/non-annotated fields, and exact reconfigurable key set.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigurationReflectionUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigurationSource.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigurationSource.java

## Purpose
Tests default methods on `ConfigurationSource` and mutable source interaction with annotated objects.

## Important APIs, Types, And Functions
APIs under test include prefix matching with and without prefix trimming, `getObject`, `reconfigure`, and set-from-object behavior through the mutable implementation.

## Control Flow
The test populates `InMemoryConfigurationForTesting`, checks returned maps, creates `ConfigurationExample`, mutates the backing config, applies reconfiguration, and verifies only the reconfigurable dynamic field changes. It also covers a key whose suffix includes the prefix text.

## State And Persistence
State is in the in-memory map and injected `ConfigurationExample` instances.

## Dependencies And Integration Points
Validates `ConfigurationSource`, `MutableConfigurationSource`, `ConfigurationReflectionUtil`, and `ReconfigurableConfig` integration.

## Risks
Does not cover all typed getters or class loading. The reconfiguration test depends on default injection values remaining stable.

## Test Signals
Signals include prefix map correctness, dynamic-only reconfiguration, and object-to-configuration write-back for prefix-containing names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestConfigurationSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestReconfigurableConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestReconfigurableConfig.java

## Purpose
Focused test for `ReconfigurableConfig.reconfigureProperty`.

## Important APIs, Types, And Functions
Uses `ConfigurationExample` created from `InMemoryConfigurationForTesting` and asserts the dynamic field changes after direct property reconfiguration.

## Control Flow
The test creates a default-injected object, calls `reconfigureProperty` with the dynamic key and new value, then reads the getter.

## State And Persistence
State is the mutable field inside `ConfigurationExample`; no external persistence.

## Dependencies And Integration Points
Covers the base class and reflection utility path for single-property reconfiguration.

## Risks
Only the successful path is covered. Unknown keys, non-reconfigurable keys, bad values, and post-construct rollback are not exercised.

## Test Signals
Signals include direct dynamic property update and preservation of the reflective conversion path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/TestReconfigurableConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/package-info.java

## Purpose
Package documentation marker for configuration unit tests.

## Important APIs, Types, And Functions
No public APIs beyond the test package declaration.

## Control Flow
Used only by Javadoc/checkstyle/package validation.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Groups tests for the `org.apache.hadoop.hdds.conf` package.

## Risks
Risk is negligible aside from stale documentation or license/package mismatch.

## Test Signals
Signals are compile, license, and checkstyle success.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/config/src/test/java/org/apache/hadoop/hdds/conf/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/dev-support/findbugsExcludeFile.xml

## Purpose
SpotBugs/FindBugs exclusion filter for the container-service module.

## Important APIs, Types, And Functions
Contains an empty `<FindBugsFilter>` root, meaning no module-specific exclusions are currently configured.

## Control Flow
The Maven SpotBugs plugin loads this file from `${basedir}/dev-support/findbugsExcludeFile.xml` during analysis.

## State And Persistence
No runtime state; it is build-time XML configuration.

## Dependencies And Integration Points
Integrated with `container-service/pom.xml` SpotBugs plugin configuration.

## Risks
An empty filter is safe but gives no local suppression mechanism. If future exclusions are needed, malformed XML can break static analysis.

## Test Signals
Signals include SpotBugs plugin successfully loading the file and no unintended suppressions in analysis reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/pom.xml

## Purpose
Maven descriptor for `hdds-container-service`, the datanode/container runtime module.

## Important APIs, Types, And Functions
Declares dependencies on Jackson, Guava, protobuf, Hadoop auth/common/HDFS, HDDS common/client/config/framework/interface modules, Ratis client/server/grpc/netty/proto, RocksDB JNI, Netty, OpenTelemetry, SnakeYAML, docs, runtime zstd/log4j extras/JAXB/HDFS client, and test jars/utilities.

## Control Flow
Build config wires SpotBugs with the module exclusion file, enables `ConfigFileGenerator` as the selected annotation processor, overrides the root enforcer annotation ban for selected processors, and unpacks shared web static assets and docs into the datanode webapp during prepare-package.

## State And Persistence
Build outputs include the container-service jar, generated config metadata, webapp static/docs resources, and test classpath artifacts.

## Dependencies And Integration Points
This module integrates datanode service startup, container RPC handling, Ratis replication, RocksDB metadata, web UI endpoints, metrics, security, and configuration generation.

## Risks
Dependency breadth increases classpath and shading/version risks. Annotation processor selection must stay aligned with banned-import rules. Web asset unpacking couples package output to `hdds-server-framework` and `hdds-docs` artifacts.

## Test Signals
Signals include full module compile/test, annotation-generated default XML, SpotBugs load of the empty filter, enforcer success, and packaged webapp resources.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/freon/FakeRatisFollower.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/freon/FakeRatisFollower.java

## Purpose
Test/support fake Ratis follower used by instrumented Freon tests to replace real outgoing Ratis gRPC calls.

## Important APIs, Types, And Functions
Static APIs are `appendEntries(RaftPeerId, StreamObserver<AppendEntriesReplyProto>)` and `requestVote(RaftPeerId, RequestVoteRequestProto)`. It reads optional `RATIS_SIMULATED_LATENCY` from the environment.

## Control Flow
AppendEntries returns a stream observer that tracks the maximum log index seen, derives follower commit from commit info and max index, builds successful append replies, optionally sleeps, and sends replies to the response handler. RequestVote returns a successful vote reply for the candidate term.

## State And Persistence
State is static simulated latency and per-append-stream `maxIndex`. No durable persistence.

## Dependencies And Integration Points
Depends on Apache Ratis protobufs, gRPC stream observer, `RaftPeerId`, and Freon test instrumentation.

## Risks
The fake always succeeds and ignores errors/completion, so it cannot model rejection, term changes, or network failures. `System.out.println` in request vote can pollute test logs. Static latency is process-wide.

## Test Signals
Signals include Freon standalone/follower simulations, append reply match/next index behavior, vote success, and latency-injected benchmark runs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/freon/FakeRatisFollower.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/freon/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/freon/package-info.java

## Purpose
Package documentation for Freon instrumentation helpers in container-service.

## Important APIs, Types, And Functions
No APIs beyond the package declaration and Javadoc reference to tests such as `LeaderAppendLogEntryGenerator`.

## Control Flow
Used by documentation and package validation.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Groups helper classes such as `FakeRatisFollower`.

## Risks
Risk is stale documentation as Freon instrumentation evolves.

## Test Signals
Signals are compile, Javadoc, and license/checkstyle success.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/freon/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/scm/VersionInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/scm/VersionInfo.java

## Purpose
Small version registry for SCM metadata in this module.

## Important APIs, Types, And Functions
Static APIs `getAllVersions()` and `getLatestVersion()` expose immutable copies from a private `VERSION_INFOS` array. Instance getters expose description and version. `DESCRIPTION_KEY` names the metadata key.

## Control Flow
Callers request all versions or the latest; the current implementation contains a single version with numeric version 1.

## State And Persistence
Version entries are immutable private objects. The array is cloned for callers to avoid direct mutation.

## Dependencies And Integration Points
Related to layout/version tracking code in HDDS/SCM, though this class is minimal in the subset.

## Risks
Adding versions requires preserving ascending order because `getLatestVersion()` returns the last array element. The class name overlaps with other HDDS version info types.

## Test Signals
Signals include tests that latest version is the expected final element and callers cannot mutate the internal array.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/scm/VersionInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/scm/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/scm/package-info.java

## Purpose
Package documentation for `org.apache.hadoop.hdds.scm` classes in container-service.

## Important APIs, Types, And Functions
No APIs beyond package declaration.

## Control Flow
Used by Javadoc and package checks.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Applies to the local SCM version-info class in this module.

## Risks
Documentation can become too vague if more SCM classes are added here.

## Test Signals
Signals are package compile and documentation generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/scm/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/DNMXBean.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/DNMXBean.java

## Purpose
JMX management interface for datanode runtime information.

## Important APIs, Types, And Functions
Extends `ServiceRuntimeInfo` and declares getters for hostname, datanode UUID, client RPC port, HTTP port, and HTTPS port.

## Control Flow
`HddsDatanodeService` fills a `DNMXBeanImpl` during startup and registers it with JMX so management clients can read the values.

## State And Persistence
No implementation state in the interface; state is held by the bean implementation and service runtime base.

## Dependencies And Integration Points
Integrated with Hadoop/HDDS metrics and JMX via `HddsUtils.registerWithJmxProperties`.

## Risks
String-returning ports are simple but require service startup to set them after bind. Missing HTTP/HTTPS policy branches may leave nulls.

## Test Signals
Signals include MXBean registration, visible hostname/UUID/ports in JMX, and runtime info inherited from `ServiceRuntimeInfo`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/DNMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/DNMXBeanImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/DNMXBeanImpl.java

## Purpose
Concrete JMX bean storing datanode identity, ports, and inherited service runtime/version information.

## Important APIs, Types, And Functions
Extends `ServiceRuntimeInfoImpl`, implements `DNMXBean`, and provides getters/setters for host name, datanode UUID, client RPC port, HTTP port, and HTTPS port.

## Control Flow
The datanode service constructs this bean with HDDS version info, sets start time and identity/ports as services bind, and registers it with JMX.

## State And Persistence
Mutable in-memory string fields hold identity and port values. Persistence is external only through JMX visibility.

## Dependencies And Integration Points
Depends on HDDS `VersionInfo` and service runtime base classes. Used directly by `HddsDatanodeService`.

## Risks
No synchronization protects setters/getters, though startup writes are mostly single-threaded. Nulls are possible for disabled or failed servers.

## Test Signals
Signals include service startup setting each field, JMX reads after HTTP/RPC bind, and unregistering the bean during shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/DNMXBeanImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeClientProtocolServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeClientProtocolServer.java

## Purpose
Hadoop protobuf RPC server exposing datanode client-side administrative protocols, specifically reconfiguration and optional disk balancer protocol.

## Important APIs, Types, And Functions
Constructor binds an `RPC.Server`, updates datanode client RPC port, and refreshes ACLs when Hadoop service authorization is enabled. Public APIs are `start`, `stop`, `join`, and `getClientRpcAddress`.

## Control Flow
Server creation sets protobuf RPC engines, reads handler/read-thread counts from config, builds a reconfigure protocol blocking service, starts the RPC server, and conditionally adds disk balancer PB protocol to the same server.

## State And Persistence
State is the bound `RPC.Server`, resolved client RPC address, and configuration reference. The datanode details object is updated with the bound port.

## Dependencies And Integration Points
Integrates with `ReconfigurationHandler`, `DiskBalancerProtocolServer`, Hadoop IPC, HDDS server utilities, ACL policy provider, and datanode details ports.

## Risks
Port/address resolution and ACL refresh must happen after bind. Stop catches and logs errors but does not propagate. Disk balancer is optional and null-safe.

## Test Signals
Signals include successful bind to configured or fallback address, datanode port update, reconfigure and disk balancer RPC calls, ACL refresh under authorization, and clean stop/join.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeClientProtocolServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeHttpServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeHttpServer.java

## Purpose
Datanode HTTP server wrapper providing standard monitoring endpoints such as `/conf`, `/prom`, and profiler endpoints.

## Important APIs, Types, And Functions
Extends `BaseHttpServer` with service name `hddsDatanode` and overrides config-key accessors for HTTP address, bind host, enabled flag, auth type, and auth config prefix.

## Control Flow
The datanode service constructs and starts it during startup, then reads bound HTTP/HTTPS addresses based on `HttpConfig.Policy` to publish ports in datanode details and JMX.

## State And Persistence
State is inherited from `BaseHttpServer`; this class itself adds no fields.

## Dependencies And Integration Points
Depends on `MutableConfigurationSource`, HDDS HTTP server framework, and `HddsConfigKeys`.

## Risks
Misconfigured bind/auth keys affect endpoint exposure. Startup failures are caught by `HddsDatanodeService`, which may continue without HTTP endpoints.

## Test Signals
Signals include HTTP/HTTPS bind, endpoint availability, auth behavior, published datanode ports, and clean shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeService.java

## Purpose
Main Ozone datanode service entry point and service plugin that initializes identity, security, layout storage, reconfiguration, RPC/HTTP servers, plugins, metrics, Ratis/container state machine, and shutdown behavior.

## Important APIs, Types, And Functions
Implements `Callable<Void>` and Hadoop `ServicePlugin`. Key APIs include `main`, `call`, `start(Object)`, `start(OzoneConfiguration)`, `start`, `stop`, `join`, `close`, `initializeCertificateClient`, `saveNewCertId`, and reconfiguration callbacks for block deletion, replication streams, and SCM node membership.

## Control Flow
Startup activates Ozone configuration, initializes metrics, loads or creates datanode details, validates host/IP, performs Kerberos login when security is enabled, initializes datanode layout storage, certificate and secret-key clients, builds `ReconfigurationHandler`, constructs `DatanodeStateMachine`, starts HTTP and client RPC servers, loads plugins, starts the state-machine daemon, optionally starts standalone Ratis for tests, and registers the MXBean. Shutdown stops plugins, reconfiguration handler, state machine, HTTP/RPC servers, JMX, Ratis metric reporters, and secret key client.

## State And Persistence
Persistent state includes the datanode ID file, layout storage VERSION metadata, certificate serial ID persisted through `persistDatanodeDetails`, and service endpoints in datanode details. In-memory state includes config, security clients, state machine, plugin list, MXBean name, reconfiguration handler, SCM service ID, and stop flag.

## Dependencies And Integration Points
Integrates with HDDS/Ozone CLI, security, SCM security protocol, datanode state machine, volume checking, disk balancer, RPC/HTTP servers, Ozone admins, tracing reconfiguration, Ratis metrics, service plugins, and shutdown hooks.

## Risks
Startup has many partial-failure boundaries: HTTP failure is logged but not fatal, while security/authentication and layout failures are fatal. Reconfiguring SCM nodes is allowed only in RUNNING state and partial add/remove results intentionally return effective node IDs. Stop is guarded by `AtomicBoolean`, but `close` is separate. Certificate persistence failure terminates the datanode.

## Test Signals
Signals include secure and insecure startup, identity persistence, Kerberos/certificate recovery, RPC/HTTP port publication, plugin lifecycle, state-machine daemon operation, dynamic reconfiguration of delete threads/replication streams/SCM nodes, MXBean registration, and orderly shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeStopService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeStopService.java

## Purpose
Minimal callback interface for stopping an `HddsDatanodeService`.

## Important APIs, Types, And Functions
Single method `stopService()`.

## Control Flow
Implementers expose a stop hook that other components can invoke without depending on the concrete service class.

## State And Persistence
No state in the interface.

## Dependencies And Integration Points
Used as a decoupling point around datanode service lifecycle.

## Risks
The contract does not define idempotence, error handling, or close/join semantics, so implementers must document behavior.

## Test Signals
Signals are compile-time wiring and callers invoking stop without concrete datanode service dependencies.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeStopService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsPolicyProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsPolicyProvider.java

## Purpose
Hadoop service authorization policy provider for datanode RPC protocols.

## Important APIs, Types, And Functions
Singleton `getInstance()` is backed by Ratis `MemoizedSupplier`. `getServices()` returns ACL mappings for reconfiguration and disk balancer protocols.

## Control Flow
When client RPC server starts under Hadoop service authorization, it refreshes service ACLs using this provider.

## State And Persistence
State is a memoized singleton and static immutable list of `Service` mappings.

## Dependencies And Integration Points
Depends on Hadoop `PolicyProvider`, HDDS ACL config keys, `ReconfigureProtocol`, `DiskBalancerProtocol`, and Ratis memoized supplier.

## Risks
Adding new datanode RPC protocols requires updating this provider or ACLs will not apply. Returned array is a copy, but service objects are shared.

## Test Signals
Signals include ACL refresh, authorized/unauthorized RPC behavior for reconfigure and disk balancer, and singleton reuse.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsPolicyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/audit/DNAction.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/audit/DNAction.java

## Purpose
Enumeration of datanode audit action names for container, block, chunk, stream, checksum, and echo operations.

## Important APIs, Types, And Functions
Implements `AuditAction` and returns `toString()` from `getAction()`. Values include create/read/update/delete/list container, block and chunk operations, small file, stream init, finalize block, checksum info, and read block.

## Control Flow
Audit code can attach a typed enum value to audit records and serialize it through `getAction`.

## State And Persistence
No mutable state; enum constants are stable action identifiers.

## Dependencies And Integration Points
Integrates with Ozone audit framework and datanode command handlers.

## Risks
Renaming enum values changes audit output and can break downstream log analytics. Missing actions lead to generic or absent audit records.

## Test Signals
Signals include audit log records for each datanode operation and compatibility of action names with existing parsers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/audit/DNAction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/audit/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/audit/package-info.java

## Purpose
Package documentation for datanode audit actions.

## Important APIs, Types, And Functions
No APIs beyond package declaration and Javadoc describing `DNAction`.

## Control Flow
Used by documentation generation.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Documents the package containing datanode `AuditAction` implementations.

## Risks
Risk is stale package documentation if additional audit classes are added.

## Test Signals
Signals are compile/Javadoc/license checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/audit/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerChecksumTreeManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerChecksumTreeManager.java

## Purpose
Coordinator for reading, writing, diffing, and exposing persisted per-container checksum Merkle trees on a datanode.

## Important APIs, Types, And Functions
Important APIs include constructor, `stop`, `diff`, `read`, `updateTree`, `addDeletedBlocks`, `getContainerChecksumInfo`, `readChecksumInfo`, `getDataChecksum`, `hasDataChecksum`, and checksum file path helpers. It uses striped locks and `ContainerMerkleTreeMetrics`.

## Control Flow
Diff validates local and peer checksum info, rejects mismatched container IDs, compares sorted block lists, then sorted chunk lists, reporting missing blocks/chunks, corrupt local chunks when the peer chunk is healthy, and diverged deleted-block metadata. Writes take a per-container lock, read existing data or empty state, merge through a provided function, serialize to a tmp file, and atomically move it into place.

## State And Persistence
Persistent state is `<containerId>.tree` under the container metadata path plus tmp files during writes. In-memory state is the striped lock set and metrics object. Readers do not lock because writes use atomic rename.

## Dependencies And Integration Points
Depends on datanode configuration for lock stripes, protobuf `ContainerChecksumInfo`, container data paths, `ContainerMerkleTreeWriter`, block data, Ratis `ByteString`, and metrics utilities.

## Risks
Atomic move may fail on unsupported filesystems. `readOrCreate` overwrites unreadable trees on update, which favors recovery but can lose corrupted forensic data. Diff assumes block IDs and chunk offsets are sorted. Skipping unhealthy peer chunks avoids copying bad data but may leave local repair incomplete until another peer is queried.

## Test Signals
Signals include checksum file read/write latency and failure metrics, diff metrics, missing/corrupt/diverged report counts, concurrent updates to the same and different containers, absent tree file behavior, and reconciliation with deleted blocks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerChecksumTreeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerDiffReport.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerDiffReport.java

## Purpose
Mutable summary of differences between a local container checksum tree and a peer's tree, describing what repair actions the local replica needs.

## Important APIs, Types, And Functions
APIs add and read missing block trees, missing chunk trees by block ID, corrupt chunk trees by block ID, diverged deleted blocks, aggregate counts, `needsRepair`, and `toString`. Nested `DeletedBlock` stores block ID and data checksum.

## Control Flow
`ContainerChecksumTreeManager.diff` populates the report while walking peer/local Merkle trees. Repair code can inspect the grouped lists and maps to request or apply missing/corrupt data and deleted-block metadata.

## State And Persistence
State is in-memory lists/maps scoped to one container ID. No persistence unless serialized/logged by higher layers.

## Dependencies And Integration Points
Depends on `ContainerProtos.BlockMerkleTree` and `ChunkMerkleTree` protobuf messages.

## Risks
The report is mutable and not synchronized. Method `getNumdivergedDeletedBlocks` has a lowercase spelling inconsistency. It stores peer tree protobufs directly, so callers should treat them as immutable values.

## Test Signals
Signals include `needsRepair` true/false, accurate aggregate counts, readable `toString`, and reconciliation tests covering all four difference classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerDiffReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerMerkleTreeMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerMerkleTreeMetrics.java

## Purpose
Metrics source for Merkle tree persistence, read/diff failures, diff outcomes, identified repair items, and latency rates.

## Important APIs, Types, And Functions
Static APIs `create` and `unregister`; increment methods for write/read/diff failures, no-repair/repair diffs, missing/corrupt/diverged counts; getters for `MutableRate` latency metrics and selected counters.

## Control Flow
`create` unregisters any existing source of the same name before registering a fresh `ContainerMerkleTreeMetrics`. Manager code increments counters and records latencies through `MetricUtil.captureLatencyNs`.

## State And Persistence
Metrics live in Hadoop `DefaultMetricsSystem`; counters/rates are mutable fields injected by metrics registration.

## Dependencies And Integration Points
Used by `ContainerChecksumTreeManager` and exposed through Hadoop metrics/JMX sinks.

## Risks
Unregistering an existing source on create can disturb another active manager if multiple managers are created in the same JVM. Some counters have getters while others do not.

## Test Signals
Signals include metrics source registration/unregistration, incremented counters after simulated read/write/diff failures, latency samples, and no duplicate source registration errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerMerkleTreeMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerMerkleTreeWriter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerMerkleTreeWriter.java

## Purpose
Builder for deterministic container checksum Merkle trees from chunk checksum metadata, including live blocks and deleted-block markers.

## Important APIs, Types, And Functions
Public APIs include constructors for empty or existing tree, `addChunks`, `addBlock`, `setDeletedBlock`, `update`, `addDeletedBlocks`, and `toProto`. Nested writers aggregate block and chunk checksums. `CHECKSUM_BUFFER_SUPPLIER` uses CRC32C.

## Control Flow
Chunks are sorted by offset inside each block and blocks by block ID. Chunk leaves hash stored checksum bytes; block checksums hash block ID plus chunk checksums; container checksum hashes block checksums. Update merges deleted blocks from existing state so deletes converge and are not overwritten by later scans. Deleted block addition can compute or clear top-level checksum depending on whether a full tree existed.

## State And Persistence
In-memory state is a `TreeMap` from block ID to block writers and per-block `TreeMap` from chunk offset to chunk writer. Persistence happens only when a manager writes the resulting protobuf to disk.

## Dependencies And Integration Points
Depends on container protobufs, `ChecksumByteBufferFactory.crc32CImpl`, `BlockData`, and Ratis `ByteString`.

## Risks
Checksum semantics are order-dependent and rely on sorted maps. Duplicate chunk offsets overwrite previous values. Deleted-block convergence rules intentionally prevent undelete, which is correct for reconciliation but can preserve a mistaken delete marker. Very large containers allocate buffers proportional to block/chunk count.

## Test Signals
Signals include deterministic tree equality independent of insertion order, duplicate offset overwrite behavior, deleted-block merge behavior, top-level checksum clearing for partial deleted-block updates, and CRC32C aggregate values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerMerkleTreeWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/DNContainerOperationClient.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/DNContainerOperationClient.java

## Purpose
Client wrapper for datanode-to-datanode container-level RPCs needed by container reconciliation, currently fetching remote container checksum information.

## Important APIs, Types, And Functions
Constructor builds a `TokenHelper` and `XceiverClientManager`. Public APIs expose the manager/helper, `getContainerChecksumInfo(containerId, dn)`, `createSingleNodePipeline`, and `close`.

## Control Flow
For a peer datanode, it creates a closed single-node standalone pipeline, acquires an xceiver client, obtains a container token, calls `ContainerProtocolCalls.getContainerChecksumInfo`, rejects empty serialized responses, parses the protobuf, and releases the client in a finally block.

## State And Persistence
State is the token helper and xceiver client manager/cache. No durable persistence.

## Dependencies And Integration Points
Depends on HDDS SCM client/pipeline APIs, datanode details, security config/certificate trust manager, secret-key signer, token helper, and protobuf container protocol calls.

## Risks
Security-enabled mode requires a certificate client that can create a trust manager. Empty checksum files are treated as IO failures. The client releases with `invalidate=false`, so bad connections may remain cached unless lower layers handle failures.

## Test Signals
Signals include successful checksum fetch from a peer, token generation under secure mode, empty-response failure, invalid protobuf failure, client release on exceptions, and close releasing the manager.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/DNContainerOperationClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ReconcileContainerTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ReconcileContainerTask.java

## Purpose
Replication-supervisor task that executes one queued container reconciliation command.

## Important APIs, Types, And Functions
Extends `AbstractReplicationTask`, stores `ReconcileContainerCommand`, `DNContainerOperationClient`, and `ContainerController`, and overrides `runTask`, `getCommandForDebug`, metric name/description, `equals`, and `hashCode`.

## Control Flow
When run, it logs the task, calls `controller.reconcileContainer` with the client, container ID, and peer datanodes from the command, marks status `DONE` on success, or `FAILED` on any exception, logging elapsed time either way.

## State And Persistence
State is the command, controller/client references, inherited deadline/term/status, and no durable persistence.

## Dependencies And Integration Points
Integrates with replication supervisor scheduling, container controller repair logic, reconciliation commands from SCM, and task metrics.

## Risks
Catching all exceptions prevents task crashes but collapses all failure causes into `FAILED`. Equality compares command while hash code uses container ID, which is acceptable only if command equality is container-centric enough for sets/maps.

## Test Signals
Signals include status transitions, metric name aggregation, deadline handling inherited from the base task, successful controller invocation, failure logging, and duplicate-task behavior in supervisor collections.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ReconcileContainerTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/package-info.java

## Purpose
Package documentation for container checksum and reconciliation support.

## Important APIs, Types, And Functions
No APIs beyond package declaration.

## Control Flow
Used by Javadoc and package checks.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Groups Merkle tree writer/manager, diff report, reconciliation task, RPC client, and metrics classes.

## Risks
Documentation may lag as reconciliation logic grows.

## Test Signals
Signals include package compile and documentation generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/DatanodeLayoutStorage.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/DatanodeLayoutStorage.java

## Purpose
Datanode metadata layout storage wrapper responsible for locating and initializing datanode layout VERSION storage.

## Important APIs, Types, And Functions
Constructors initialize `Storage` for `NodeType.DATANODE` with metadata directory, datanode layout version directory, optional datanode ID, and layout version. Overrides `getCurrentDir`, `getNodeProperties`, and `setClusterId`.

## Control Flow
Startup constructs this class, checks its storage state, and initializes it if needed. Default layout version chooses the current max layout version unless an old `datanode.id` file exists without layout metadata, in which case it uses the initial layout version for upgrade compatibility.

## State And Persistence
Persistent state is the datanode layout VERSION directory under the Ozone metadata path. Cluster ID is stored in inherited storage info. No additional node properties are written.

## Dependencies And Integration Points
Depends on `Storage`, `ServerUtils.getOzoneMetaDirPath`, `HddsServerUtil.getDatanodeIdFilePath`, HDDS layout feature/version manager, and Ozone constants.

## Risks
The default layout heuristic is upgrade-sensitive: stale or misplaced datanode ID files can force initial layout. `setClusterId` mutates storage info without directly writing; caller must ensure persistence through storage lifecycle.

## Test Signals
Signals include fresh install defaulting to max layout, old-ID upgrade defaulting to initial version, VERSION initialization, cluster ID persistence, and current directory path correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/DatanodeLayoutStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/HDDSVolumeLayoutVersion.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/HDDSVolumeLayoutVersion.java

## Purpose
Small registry of datanode volume layout versions.

## Important APIs, Types, And Functions
Static APIs `getAllVersions` and `getLatestVersion`; instance getters expose version number and description. The current array contains version 1.

## Control Flow
Callers read all known volume layout versions or the latest entry; ordering of the private array determines latest.

## State And Persistence
Immutable objects in a private static array; arrays returned to callers are clones.

## Dependencies And Integration Points
Related to datanode volume formatting and storage metadata code.

## Risks
Future version additions must append in order. The class is separate from datanode metadata layout versions and can be confused with `HDDSLayoutFeature`.

## Test Signals
Signals include latest version selection, cloned array immutability, and storage code using the expected volume layout number.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/HDDSVolumeLayoutVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/BlockDeletingServiceMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/BlockDeletingServiceMetrics.java

## Purpose
Metrics holder for the datanode background block deletion service.

## Important APIs, Types, And Functions
Singleton-style static `create`/`unRegister` manage registration. Counters/gauges track successful and failed deletes, bytes deleted, out-of-order transactions, pending block counts/bytes, received transactions/retries/containers/blocks, marked/chosen blocks/containers, lock timeouts, and processed transaction success/failure counts.

## Control Flow
The block deleting service creates the metrics source, updates counters and gauges as it receives and processes delete transactions, and can render a tab-separated summary through `toString`.

## State And Persistence
Metrics live in `DefaultMetricsSystem`; a static `instance` tracks registration. Values are mutable Hadoop metrics objects.

## Dependencies And Integration Points
Depends on Hadoop metrics annotations/system and `BlockDeletingService` for source naming.

## Risks
Static singleton registration can conflict in multi-service tests if unregister is missed. Some variables named gauges are incremented rather than set, so semantic consistency depends on caller usage.

## Test Signals
Signals include registration/unregistration, counter increments during successful/failed deletes, pending gauge updates, lock-timeout count, and summary string values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/BlockDeletingServiceMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/CommandHandlerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/CommandHandlerMetrics.java

## Purpose
Dynamic metrics source exposing per-SCM-command handler runtime, queue, pool, invocation, and received-command metrics.

## Important APIs, Types, And Functions
Static `create(handlerMap)` registers a metrics source. Public APIs are `increaseCommandCount`, `getMetrics`, and `unRegister`. Inner enum `CommandMetricsMetricsInfo` defines metric descriptions.

## Control Flow
At metrics collection time, it iterates the handler map and emits one record per command handler tagged by command type, reading total/average runtime, queued count, invocation count, optional pool sizes, and the locally tracked received command count.

## State And Persistence
In-memory state is the command handler map and an `AtomicInteger` count per command type. Metrics are exposed through `DefaultMetricsSystem`.

## Dependencies And Integration Points
Depends on SCM command protobuf `Type`, command handler interface methods, and Hadoop metrics APIs.

## Risks
`increaseCommandCount` assumes the command type exists in the initial map; new handlers added later are not tracked. Reusing a single source name can conflict if multiple dispatchers exist in one JVM.

## Test Signals
Signals include metrics records for each handler, received-count increments, optional pool gauges when non-negative, and unregister behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/CommandHandlerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ContainerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ContainerMetrics.java

## Purpose
Metrics source for storage container datanode operations, bytes, latencies, closed-container bytes, delete failures, read state-machine stats, and reconciliation outcomes.

## Important APIs, Types, And Functions
Static APIs `create(conf)` and `remove`; instance methods increment operation counts, latencies, bytes, closed-container bytes, delete failure counters, force deletes, read-state-machine counters, and reconciliation counters. It implements `Closeable` to stop quantiles.

## Control Flow
Construction creates per-`ContainerProtos.Type` counters/rates and optional quantiles based on configured percentile intervals. Runtime handlers increment metrics by operation type and add latency samples.

## State And Persistence
Metrics are registered in `DefaultMetricsSystem`; per-type metric objects live in enum maps and a metrics registry. Quantiles have background resources stopped by `close`.

## Dependencies And Integration Points
Depends on HDDS metrics percentile config, Hadoop metrics registry, container protobuf operation types, and `MetricUtil`.

## Risks
The constructor reuses the same `MutableQuantiles[]` reference for every operation type, so all map entries share the final array contents; this may be unintended and can mix quantile state. Callers must close to stop quantile resources and remove to unregister.

## Test Signals
Signals include per-operation counters/bytes/latencies, configured quantile emission, closed-container byte tracking, delete failure counters, reconciliation counters, and no leaked quantile threads after close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ContainerMetrics.java -->
