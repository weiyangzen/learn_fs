# Research report: subset-b-007339

This grouped report covers Hadoop common configuration and crypto classes. Each source file section is bounded by the required reconciliation markers and is intended to be split into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Configuration.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Configuration.java`

## Purpose

`Configuration` is Hadoop's central mutable configuration container. It loads XML resources, default resources, programmatic overlays, and serialized configuration data; resolves deprecated keys; expands variables; exposes typed getters and setters; tracks final parameters and value sources; writes XML/JSON/Writable representations; and provides class/resource lookup helpers. It is public and stable because much of Hadoop and downstream applications depend on this API.

## Important APIs and Types

The top-level class implements `Iterable<Map.Entry<String,String>>` and `Writable`. Key nested types include `Resource` for classpath, URL, `Path`, `InputStream`, or `Properties` resources; `DeprecationDelta`, `DeprecatedKeyInfo`, and immutable `DeprecationContext` for key aliasing; `IntegerRanges` for range expressions; `ParsedTimeDuration`; parser helper types; and a negative class-cache sentinel. Public API surface includes `addResource`, `reloadConfiguration`, `addDefaultResource`, `get`, `getRaw`, `set`, `unset`, typed getters/setters for numeric, boolean, enum, time, storage, pattern, socket, class, password, lists, and regex queries, plus `writeXml`, `dumpConfiguration`, `readFields`, and `write`.

## Control Flow

Construction registers instances in a weak global registry and optionally loads default resources lazily. The first value access calls `getProps`, which builds `properties` and invokes `loadProps`. `loadProps` loads defaults, then each explicit `Resource`, then reapplies `overlay`. XML loading uses Woodstox with optional restricted parser settings, accepts full property elements and short-form attributes, handles `include` and fallback elements, applies deprecated-key mappings, records sources, and populates tag maps. `get` and `getRaw` first call `handleDeprecation`; `get` additionally calls `substituteVars` with bounded 20-step expansion. Setters update both `overlay` and `properties` and mirror deprecated/new aliases. Writers synthesize DOM XML or Jackson JSON while redacting sensitive values in dump paths.

## State and Persistence

Instance state includes `resources`, lazy `properties`, programmatic `overlay`, `finalParameters`, class loader, `quietmode`, system-property restriction flags, `propertyTagsMap`, and lazily allocated `updatingResource`. Static state includes default resource names, a weak registry of live configurations, class lookup caches per class loader, global tag names, and the atomic deprecation context. Persistence formats are Hadoop `Writable`, XML via `writeXml`, and JSON via `dumpConfiguration`. `InputStream` resources are consumed once then cached as `Properties` resources to make reload/copy behavior deterministic.

## Dependencies and Integration Points

This class integrates with Hadoop `FileSystem`, `Path`, `NetUtils`, `CredentialProviderFactory`, `WritableUtils`, `ReflectionUtils`, `StringUtils`, `XMLUtils`, and common key constants. It depends on Woodstox/StAX for XML parsing, W3C DOM and JAXP transformers for XML output, Jackson for JSON, SLF4J for logging, and Java security/environment/system property APIs for substitution. It is consumed across Hadoop services, clients, serializers, web UIs, crypto codec discovery, and credential lookup paths.

## Risks

Deprecation alias handling mutates loaded properties as a side effect, so ordering and synchronization matter. `get` loops over replacement names and returns the last replacement's value, which makes deprecation mapping order significant. XML include handling can reach filesystem or URLs unless restricted, making proxy-user restricted parser behavior security-sensitive. Variable substitution only detects direct self-reference and caps depth, so complex cycles fail by depth exception. `finalParameters` prevent later overrides but still require correct resource ordering. Class lookup negative caching can hide newly added classes for the same class loader. Password fallback may expose clear text if the fallback flag remains enabled. Some methods are synchronized but iteration returns snapshots, so callers should not assume strong consistency under concurrent mutation.

## Test Signals

Useful tests should cover default/core-site load order, adding resources after initial load, `InputStream` caching, final property override warnings, deprecation mirroring in get/set/unset/credential lookup, restricted parser denial of includes/DTDs, variable substitution with env defaults and cycles, typed parsing failures, storage and time unit conversion precision warnings, source tracking in XML/JSON/Writable round trips, class cache hit/miss behavior, tag extraction, and redaction of sensitive keys in configuration dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Configuration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ConfigurationWithLogging.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ConfigurationWithLogging.java`

## Purpose

`ConfigurationWithLogging` is a private diagnostic subclass of `Configuration` that logs reads and writes while redacting sensitive values. It wraps an existing configuration by invoking the copy constructor, then traces access through selected getters and `set`.

## Important APIs and Types

The constructor accepts a `Configuration` and initializes a `ConfigRedactor` from it. Overrides cover `get(String)`, `get(String,String)`, `getBoolean`, `getFloat`, `getInt`, `getLong`, and `set(String,String,String)`. It uses SLF4J logging and delegates all real behavior to `super`.

## Control Flow

Each overridden getter calls the base implementation, formats a log line with the key, resolved value, and default when present, and returns the base value unchanged. String values and defaults pass through `ConfigRedactor`; primitive values are logged directly. `set` logs the new value and optional source before calling the base setter.

## State and Persistence

State is inherited from `Configuration`, with two additional final fields: `log` and `redactor`. Copy construction means it snapshots the input configuration's loaded resources, overlays, final parameters, tag map, class loader, and quiet mode at construction time; later mutations to the original configuration are not shared.

## Dependencies and Integration Points

This class integrates with `ConfigRedactor` and the `Configuration` API. It is suitable for service code that needs audit-like visibility into configuration access without exposing secrets in logs.

## Risks

Only selected getter overloads are logged, so access through other methods such as `getTrimmed`, `getRaw`, typed collection getters, password APIs, or inherited methods may not be logged directly. Logging occurs at info level, which can be noisy and may still reveal non-redacted but operationally sensitive non-secret values. Because the wrapper is a copy, it can diverge from the source configuration.

## Test Signals

Tests should assert delegation equivalence for overridden methods, redaction of known secret keys, source text in `set`, primitive default logging, and that unoverridden methods behave exactly like a copied `Configuration`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ConfigurationWithLogging.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Configured.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Configured.java`

## Purpose

`Configured` is a small public stable base class for objects that implement Hadoop's `Configurable` contract. It stores a `Configuration` reference and gives subclasses a conventional implementation of `setConf` and `getConf`.

## Important APIs and Types

The class exposes a no-arg constructor that delegates to `Configured(null)`, a constructor accepting a `Configuration`, `setConf(Configuration)`, and `getConf()`. The stored `conf` field is private and not copied.

## Control Flow

Construction immediately calls `setConf`, allowing subclasses that override `setConf` to participate in initialization. After construction, callers can replace the held configuration at any time through `setConf`.

## State and Persistence

The only state is the `Configuration` reference. There is no synchronization, validation, serialization, cloning, or persistence.

## Dependencies and Integration Points

It depends on the `Configurable` interface and `Configuration`. Many Hadoop tools, services, and helper classes extend this class so they can be initialized by reflection utilities or service frameworks that detect `Configurable`.

## Risks

The no-arg constructor leaves `conf` null, so subclasses must handle null or install defaults. Because the reference is mutable and not synchronized, it is unsuitable as a thread-safe configuration holder without external discipline.

## Test Signals

Tests should verify constructor assignment, replacement through `setConf`, null handling, and subclass override behavior during construction if subclasses depend on that hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Configured.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Reconfigurable.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Reconfigurable.java`

## Purpose

`Reconfigurable` defines the interface for Hadoop components whose `Configuration` can be changed at runtime. It extends `Configurable` with methods for applying one property change and discovering which properties are allowed to change.

## Important APIs and Types

The core methods are `reconfigureProperty(String property, String newVal)`, `isPropertyReconfigurable(String property)`, and `getReconfigurableProperties()`. `newVal == null` means reset the property to its default value.

## Control Flow

Implementations are expected to validate whether a property is reconfigurable, apply the new value to internal state, then update the backing `Configuration`. If the property is not allowed or the value cannot be applied, implementations throw `ReconfigurationException`.

## State and Persistence

The interface owns no state. Implementing classes decide whether changes are only in-memory or are also reflected in external files or service-specific persistent state. The common base implementation updates only the in-memory `Configuration`.

## Dependencies and Integration Points

This is used by `ReconfigurableBase`, `ReconfigurationServlet`, and management tooling. Service daemons expose an instance through servlet context attributes so administrators can compare current and reloaded configuration and apply allowed changes.

## Risks

Correctness depends entirely on implementers keeping `isPropertyReconfigurable`, `getReconfigurableProperties`, and `reconfigureProperty` consistent. A property can be marked reconfigurable but still fail if the implementation cannot safely update all derived runtime state.

## Test Signals

Tests should exercise both allowed and disallowed properties, null default reset semantics, propagation to the backing `Configuration`, and failure paths that preserve old runtime state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/Reconfigurable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurableBase.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurableBase.java`

## Purpose

`ReconfigurableBase` is the standard helper base for runtime reconfiguration. It extends `Configured`, implements `Reconfigurable`, provides synchronous single-property changes, and adds a background task that reloads a fresh configuration, computes differences, and applies allowed changes.

## Important APIs and Types

Subclasses must implement `getNewConf()`, `getReconfigurableProperties()`, and `reconfigurePropertyImpl(String,String)`. Public APIs include `startReconfigurationTask`, `getReconfigurationTaskStatus`, `shutdownReconfigurationTask`, final `reconfigureProperty`, `isPropertyReconfigurable`, and visible-for-testing hooks for the `ReconfigurationUtil`.

## Control Flow

`startReconfigurationTask` synchronizes on `reconfigLock`, rejects stopped or already-running state, creates a daemon `ReconfigurationThread`, starts it, and records `startTime`. The thread captures old and new configs, asks `ReconfigurationUtil` for changed properties, redacts values for logging, skips non-reconfigurable changes, calls `reconfigurePropertyImpl` for each allowed change, and updates or unsets the old configuration. It records a map from `PropertyChange` to optional error message, marks `endTime`, and clears `reconfigThread`. The final `reconfigureProperty` method performs the same core operation for one property under `getConf()` synchronization.

## State and Persistence

State includes the backing `Configuration`, a replaceable `ReconfigurationUtil`, a background thread reference, `shouldRun`, `reconfigLock`, start/end timestamps, and the latest immutable status map. Persistence is in-memory only; changes update the current `Configuration` but do not rewrite configuration files.

## Dependencies and Integration Points

It integrates with `ReconfigurationUtil.PropertyChange`, `ReconfigurationTaskStatus`, `ConfigRedactor`, `SubjectInheritingThread`, `Time`, Guava-compatible `Maps`, and service-specific subclasses in HDFS/YARN daemons. Web or RPC management layers can trigger and poll the task.

## Risks

`shutdownReconfigurationTask` sets `reconfigThread` to null before joining, so status polling can report stopped state while a captured thread is still finishing. Non-reconfigurable changes are skipped and not recorded in the status map, which may make status incomplete for operators. Exceptions from `reconfigurePropertyImpl` are captured per property, but partially applied earlier properties remain applied. `shouldRun` is never reset to true after shutdown. Synchronization separates `reconfigLock` from `getConf()` locking, so subclass implementations must avoid lock-order problems.

## Test Signals

Tests should cover single-property success/failure, disallowed properties, null reset, background task rejection when running or stopped, status timestamps and optional error messages, redacted logging, subclass effective values differing from requested values, and interruption/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurableBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationException.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationException.java`

## Purpose

`ReconfigurationException` signals that a runtime configuration change could not be applied. It carries the property name, requested new value, old value, and optionally a cause.

## Important APIs and Types

Constructors include a generic no-arg failure, a property/new/old constructor, and a property/new/old/cause constructor. Accessors are `getProperty`, `getNewValue`, and `getOldValue`.

## Control Flow

The property-specific constructors build a message with `constructMessage`, then store the three value fields. The class itself has no recovery behavior; callers catch it to report or store failure information.

## State and Persistence

The exception stores three mutable-looking private strings, though there are no setters. It is serializable through Java exception serialization with `serialVersionUID = 1L`.

## Dependencies and Integration Points

It is thrown by `Reconfigurable` implementations and caught by `ReconfigurableBase` and `ReconfigurationServlet`. Service code can wrap lower-level errors as the cause.

## Risks

The constructed message includes raw property values, which can expose secrets if a sensitive property is reconfigured and the message is logged or returned to a servlet client. Message formatting around missing old/new values is minimal and can produce less readable text.

## Test Signals

Tests should assert constructors populate fields, preserve causes, and generate expected messages for old-only, new-only, and both-value cases. Sensitive-value redaction should be tested at callers, because this exception does not redact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationServlet.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationServlet.java`

## Purpose

`ReconfigurationServlet` is an HTML servlet for viewing proposed configuration changes and applying approved runtime reconfiguration to a registered `Reconfigurable` component.

## Important APIs and Types

The servlet exposes `CONF_SERVLET_RECONFIGURABLE_PREFIX`, overrides `doGet` and `doPost`, and uses private helpers `getReconfigurable`, `printHeader`, `printFooter`, `printConf`, `getParams`, and `applyChanges`. It extends `HttpServlet`.

## Control Flow

The servlet looks up the target `Reconfigurable` from the servlet context using the prefix plus request servlet path. `doGet` creates a fresh `Configuration`, compares it with the current component configuration via `ReconfigurationUtil.getChangedProperties`, renders each change, marks non-reconfigurable properties in red, and includes hidden form fields for allowed changes. `doPost` creates a new fresh configuration again, then iterates submitted parameters under synchronization on the old configuration. It only applies a submitted value if it still matches the freshly loaded value or represents default/null/empty reset, then calls `reconfigureProperty`; otherwise it reports that the value changed since approval.

## State and Persistence

The servlet stores no per-request state beyond inherited servlet state. Runtime changes are delegated to the target `Reconfigurable`; it does not persist changes to configuration files.

## Dependencies and Integration Points

It depends on Java Servlet APIs, Apache Commons Text HTML escaping/unescaping, `ReconfigurationUtil`, `Configuration`, `Reconfigurable`, `ReconfigurationException`, and `StringUtils.stringifyException`. It is integrated by daemon web apps that publish a `Reconfigurable` context attribute.

## Risks

Authentication and authorization are not handled in this class, so deployment must protect the servlet. Hidden form fields trust client-submitted names and values but revalidate against a freshly loaded configuration before applying. Values are HTML-escaped for rendering, but exception responses may include raw exception messages from lower layers. A missing context attribute causes null dereference. The page uses simple HTML and does not redact property values, so it can expose sensitive configuration unless upstream access controls and property choice prevent it.

## Test Signals

Tests should cover context lookup, GET rendering for allowed/disallowed changes, HTML escaping of names/values, POST reset semantics, stale-value rejection, exception-to-500 behavior, synchronization with the old configuration, and access-control behavior in the hosting web app.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationTaskStatus.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationTaskStatus.java`

## Purpose

`ReconfigurationTaskStatus` is a lightweight status value object for the most recent background reconfiguration task.

## Important APIs and Types

The constructor accepts `startTime`, `endTime`, and a map from `ReconfigurationUtil.PropertyChange` to `Optional<String>` error messages. Public methods are `hasTask`, `stopped`, `getStartTime`, `getEndTime`, and `getStatus`.

## Control Flow

`hasTask` reports whether any task has started by checking `startTime > 0`. `stopped` reports that a task has finished by checking `endTime > 0`. A running task is represented by nonzero start, zero end, and null status.

## State and Persistence

The object stores package-visible `startTime` and `endTime`, plus a final status map reference. It does not defensively copy the map, so immutability depends on the producer. There is no persistence.

## Dependencies and Integration Points

It is produced by `ReconfigurableBase.getReconfigurationTaskStatus` and consumed by management APIs/tools. It uses `Optional` to distinguish success from a property-specific error message.

## Risks

Null status is a legitimate running-state value, so clients must check `stopped()` before iterating. Package-visible timestamp fields are mutable within the package. Status contains `PropertyChange` keys whose class does not override equality/hashCode, which is acceptable for direct reporting but not semantic lookup across separately constructed changes.

## Test Signals

Tests should verify running, never-started, and completed states; null status handling; success/error optional semantics; and that callers do not assume `getStatus()` is non-null before completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationTaskStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationUtil.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationUtil.java`

## Purpose

`ReconfigurationUtil` compares two `Configuration` instances and returns the changed properties needed by runtime reconfiguration workflows.

## Important APIs and Types

The nested `PropertyChange` type holds public `prop`, `oldVal`, and `newVal` fields. `getChangedProperties(Configuration newConf, Configuration oldConf)` is the static comparator, and `parseChangedProperties` is an instance wrapper used for test injection by `ReconfigurableBase`.

## Control Flow

The comparator first iterates old configuration entries, checking each old value against `newConf.getRaw(prop)` and adding a change when the new raw value is missing or different. It then iterates new configuration entries and adds changes for properties where `oldConf.get(prop)` is null, representing newly introduced settings. A map keyed by property name deduplicates changes from both passes.

## State and Persistence

The utility itself is stateless. `PropertyChange` is mutable and has identity equality because it does not override `equals` or `hashCode`.

## Dependencies and Integration Points

It depends on `Configuration` iteration and raw/value getters. It is used by `ReconfigurableBase` and `ReconfigurationServlet` to compute differences between current in-memory config and freshly loaded defaults/resources.

## Risks

The first pass compares old resolved values with new raw values, while the second pass uses `oldConf.get(prop)`; variable substitution and deprecation side effects can therefore affect comparisons. Because `PropertyChange` is mutable and identity-based, it is best suited for reporting, not set algebra. Changes to final/non-reconfigurable properties are included here and filtered later.

## Test Signals

Tests should cover changed, added, removed, unchanged, null/default, substituted-value, and deprecated-key scenarios, plus duplicate avoidance when a property appears in both passes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/StorageSize.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/StorageSize.java`

## Purpose

`StorageSize` pairs a numeric double value with a `StorageUnit` and parses human-readable storage size strings used by `Configuration.getStorageSize`.

## Important APIs and Types

The constructor stores `StorageUnit unit` and `double value`. Public methods are static `parse(String)`, `getUnit`, and `getValue`.

## Control Flow

`parse` rejects blank input, lowercases and trims it, then scans `StorageUnit.values()` for a suffix match against long name, short name, or single-character suffix. It then chooses the longest suffix match in long-name, short-name, suffix-character order, strips that suffix, parses the remaining numeric part as a `double`, and returns a new `StorageSize`.

## State and Persistence

Instances are immutable: both fields are final and no setters exist. No persistence is implemented.

## Dependencies and Integration Points

It depends on `StorageUnit`, `Locale.ENGLISH`, and Apache Commons `isNotBlank`. It is called by `Configuration` storage-size getters to parse strings like `100MB` before converting to target units.

## Risks

The initial unit scan relies on `StorageUnit` declaration order, especially because bytes uses the short name/suffix `b` and can match many longer suffixes if ordered incorrectly. The substring uses the original input length rather than the sanitized length, which is fine for same-length trim/lowercase content after trim but should be protected by tests around leading/trailing whitespace. The parser accepts any `Double.parseDouble` format after suffix stripping, including negative and special values if Java accepts them.

## Test Signals

Tests should cover long, short, and one-character suffixes for every unit; case and whitespace normalization; invalid or missing suffixes; decimal values; byte suffix ambiguity; and integration with `Configuration.getStorageSize`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/StorageSize.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/StorageUnit.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/StorageUnit.java`

## Purpose

`StorageUnit` is an enum that defines binary storage units from bytes through exabytes and provides conversion methods among them.

## Important APIs and Types

Enum constants are `EB`, `PB`, `TB`, `GB`, `MB`, `KB`, and `BYTES`. Each constant implements `toBytes`, `toKBs`, `toMBs`, `toGBs`, `toTBs`, `toPBs`, `toEBs`, `getLongName`, `getShortName`, `getSuffixChar`, `getDefault`, and `fromBytes`. Shared helpers `divide` and `multiply` use `BigDecimal` and scale to four decimal places.

## Control Flow

Conversions either multiply by the source unit's byte multiplier or divide by the target multiplier. `getDefault` returns the value interpreted in that enum's native unit. `toString` returns the long name. The enum declaration order intentionally puts `BYTES` last so parsing code can match longer unit suffixes before `b`.

## State and Persistence

The enum stores no mutable instance state. Static constants define binary multipliers and precision. There is no persistence beyond string names exposed by methods.

## Dependencies and Integration Points

It is used by `StorageSize.parse` and `Configuration` storage-size getters/setters. It depends on `BigDecimal` and `RoundingMode.HALF_UP` for rounded double conversions.

## Risks

Every conversion returns `double`, so large values may still lose precision even though intermediate arithmetic uses `BigDecimal`. `new BigDecimal(double)` preserves binary floating imprecision rather than decimal text intent. Four-decimal rounding can truncate meaningful precision in configuration values. Reordering enum constants can break suffix parsing.

## Test Signals

Tests should verify all pairwise unit conversions, precision/rounding behavior, very large values, negative values if allowed, `getDefault` semantics, suffix strings, and preservation of enum order assumptions used by `StorageSize`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/StorageUnit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CipherOption.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CipherOption.java`

## Purpose

`CipherOption` is a private data carrier used by client/server negotiation to describe a cipher suite and optional inbound/outbound keys and IVs.

## Important APIs and Types

The fields are final `CipherSuite suite`, `byte[] inKey`, `byte[] inIv`, `byte[] outKey`, and `byte[] outIv`. Constructors accept either only a suite or all five values. Getters expose each field.

## Control Flow

There is no behavior beyond construction and access. The suite-only constructor delegates with null key/IV arrays.

## State and Persistence

Instances are shallowly immutable: field references are final, but byte arrays are not cloned or defensively copied. There is no serialization code in this class.

## Dependencies and Integration Points

It depends on `CipherSuite` and is used by higher-level RPC/data-transfer negotiation paths that exchange negotiated cipher material.

## Risks

Because arrays are returned directly, callers can mutate keys and IVs after construction or retrieval. This is security-sensitive and requires ownership discipline by callers. Null arrays are valid and must be handled in consumers.

## Test Signals

Tests should verify suite-only null fields, full constructor field exposure, and consumer behavior for null and non-null key/IV data. Security reviews should check whether callers need defensive copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CipherOption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CipherSuite.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CipherSuite.java`

## Purpose

`CipherSuite` defines supported cipher suite metadata for Hadoop crypto streams and protocol negotiation.

## Important APIs and Types

Constants are `UNKNOWN`, `AES_CTR_NOPADDING`, and `SM4_CTR_NOPADDING`. Each stores a JCE-style name and algorithm block size. Methods include `setUnknownValue`, `getUnknownValue`, `getName`, `getAlgorithmBlockSize`, `convert(String)`, `getConfigSuffix`, and `toString`.

## Control Flow

`convert` linearly scans enum values and matches by exact `getName`, throwing `IllegalArgumentException` when no name matches. `getConfigSuffix` splits the JCE-style name on `/`, lowercases each part through Hadoop `StringUtils`, and prepends dots to build keys such as `.aes.ctr.nopadding`.

## State and Persistence

Enum instances are mostly immutable except for `unknownValue`, which can be set on an enum constant. That mutability is used when preserving unknown wire values during protocol decoding.

## Dependencies and Integration Points

`CryptoCodec`, `CryptoStreamUtils`, `JceAesCtrCryptoCodec`, and stream classes depend on suite name and block size. Configuration keys for codec class discovery are derived from `getConfigSuffix`.

## Risks

`UNKNOWN.getUnknownValue()` unboxes an `Integer` and can throw `NullPointerException` if called before `setUnknownValue`. `convert` is case-sensitive and name-based, not enum-name-based. Adding suites requires configuration defaults, codec implementations, and `CryptoStreamUtils.checkCodec` updates if streams should accept them.

## Test Signals

Tests should cover name conversion success/failure, config suffix construction, unknown value preservation, block-size expectations, and behavior when new suite constants are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CipherSuite.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoCodec.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoCodec.java`

## Purpose

`CryptoCodec` is the abstract base for Hadoop cryptographic codecs. It encapsulates cipher-suite identity, encryptor/decryptor creation, CTR IV calculation, and secure random generation.

## Important APIs and Types

Static factories are `getInstance(Configuration)` and `getInstance(Configuration,CipherSuite)`. The private `getCodecClasses` reads configured codec class names. Abstract methods are `getCipherSuite`, `createEncryptor`, `createDecryptor`, `calculateIV`, and `generateSecureRandom`. The class also implements `Configurable` and `Closeable`.

## Control Flow

`getInstance(conf)` reads the configured cipher suite key and converts it to `CipherSuite`. `getInstance(conf,suite)` obtains candidate codec classes from suite-specific configuration keys, instantiates each with `ReflectionUtils.newInstance`, and returns the first instantiated codec whose reported suite name matches the requested suite. Unavailable or mismatched classes are logged at performance-advisory debug level and skipped.

## State and Persistence

The abstract class owns no fields except a static logger. Concrete codecs own provider, random, and cipher state. There is no persistence.

## Dependencies and Integration Points

It depends on Hadoop configuration constants, reflection utilities, `PerformanceAdvisory`, and Guava-compatible `Splitter`. It integrates directly with `CryptoInputStream`, `CryptoOutputStream`, HDFS encryption zones, and codec class configuration keys for AES and SM4.

## Risks

Factory lookup returns null when no usable codec is configured, so callers must fail clearly. Candidate instantiation exceptions are swallowed into debug logs, which can hide provider or classpath failures unless debug logging is enabled. Suite matching compares names rather than enum identity. Codec implementations must make `generateSecureRandom` thread-safe.

## Test Signals

Tests should cover default AES/SM4 class discovery, invalid class names, classes not extending `CryptoCodec`, unavailable provider failures, suite mismatch filtering, null return behavior, and configuration-driven factory selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoInputStream.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoInputStream.java`

## Purpose

`CryptoInputStream` wraps an input stream and decrypts CTR-mode ciphertext into plaintext while preserving a one-to-one byte mapping between encrypted and clear data. It supports sequential reads, seeks, positioned reads, byte-buffer reads, enhanced byte-buffer access, unbuffering, stream capabilities, and IO statistics delegation.

## Important APIs and Types

The class extends `FilterInputStream` and implements `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `ReadableByteChannel`, `CanUnbuffer`, `StreamCapabilities`, `ByteBufferPositionedReadable`, and `IOStatisticsSource`. It owns a `CryptoCodec`, main `Decryptor`, direct `inBuffer` and `outBuffer`, stream offset, padding, cloned key and IV material, and pools for direct buffers and decryptors used by positioned reads.

## Control Flow

Construction validates that the codec is AES/CTR or SM4/CTR, floors buffer size to a block multiple, clones key/IV, allocates direct buffers, creates a decryptor, and initializes it for the current stream offset. Sequential `read(byte[],off,len)` drains `outBuffer` if possible; otherwise it reads ciphertext into `inBuffer` using byte-buffer-capable APIs when supported, updates `streamOffset`, decrypts, handles padding, and returns plaintext from `outBuffer`. `seek` either repositions within already decrypted buffered data or seeks the wrapped stream and resets decryptor state. Positioned reads delegate to wrapped positioned APIs, then decrypt the returned range using local buffers/decryptors without changing the main stream offset. Byte-buffer read paths decrypt in place over the bytes just read.

## State and Persistence

State is in-memory stream state only: offset, padding, decryptor context, direct buffers, cached temporary heap buffer, and pools. Key and IV arrays are cloned at construction. `close` closes the wrapped stream through `super.close`, frees direct buffers, closes the codec, and marks closed. `unbuffer` frees pooled buffers/decryptors and delegates unbuffering.

## Dependencies and Integration Points

It integrates with Hadoop filesystem stream interfaces, `CryptoCodec`, `Decryptor`, `CryptoStreamUtils`, direct buffer cleaner utilities, `StreamCapabilitiesPolicy`, and IO statistics support. It can wrap HDFS or local streams and preserve enhanced capabilities when the underlying stream exposes them.

## Risks

The class is documented as not thread-safe except positioned read helpers. Offset, padding, and decryptor context must remain exactly aligned; off-by-one errors corrupt all following bytes. `setDropBehind` checks `CanSetReadahead` before casting to `CanSetDropBehind`, which appears suspicious and should be covered by tests. Direct buffers require explicit cleanup and may leak until GC if close is missed. Positioned byte-buffer decryption updates local padding using `filePosition + length` in one branch, which deserves careful tests over multi-chunk partial reads. `close` closes the codec, so sharing codec instances across streams can be risky unless callers manage lifecycle.

## Test Signals

Tests should cover sequential reads across block boundaries, nonzero initial stream offsets, seek within/outside buffered plaintext, skip semantics, positioned read and readFully for byte arrays and byte buffers, direct and heap `ByteBuffer` reads, enhanced buffer read/release, EOF behavior with unread decrypted data, unbuffer cleanup, capability delegation, direct-buffer cleanup on close, and AES/SM4 compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoOutputStream.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoOutputStream.java`

## Purpose

`CryptoOutputStream` wraps an output stream and encrypts plaintext into CTR-mode ciphertext with a one-to-one byte mapping. It tracks stream offset so encryption can start at arbitrary positions.

## Important APIs and Types

The class extends `FilterOutputStream` and implements `Syncable`, `CanSetDropBehind`, `StreamCapabilities`, and `IOStatisticsSource`. Constructors accept a wrapped stream, codec, optional buffer size, key, IV, stream offset, and a flag controlling whether closing this wrapper closes the underlying stream. Public methods include `write`, `flush`, `close`, `hflush`, `hsync`, `setDropBehind`, `hasCapability`, `getIOStatistics`, and `getWrappedStream`.

## Control Flow

Construction validates codec and buffer size, clones key/IV, allocates direct input/output buffers, creates an encryptor, and initializes it with IV derived from `streamOffset / blockSize` plus padding at `streamOffset % blockSize`. `write(byte[],off,len)` fills `inBuffer`; when full, `encrypt` flips it, encrypts to `outBuffer`, skips leading padding once, writes encrypted bytes to the underlying stream via a temporary heap array, advances `streamOffset`, and reinitializes if the encryptor reset its context. `flush` encrypts pending buffered data before flushing. `hflush` and `hsync` flush encryption state first, then delegate sync calls when supported.

## State and Persistence

State includes direct buffers, cloned key and initial/current IV, current stream offset, padding, one encryptor, optional heap temp buffer, closed flag, and `closeOutputStream`. There is no independent persistence; encrypted bytes are written to the wrapped stream.

## Dependencies and Integration Points

It integrates with `CryptoCodec`, `Encryptor`, `CryptoStreamUtils`, Hadoop `Syncable`, stream capabilities helpers, drop-behind support, and IO statistics. HDFS clients use this style of wrapper to encrypt file data while preserving file offsets.

## Risks

The class is not thread-safe despite synchronized core methods matching `DFSOutputStream` behavior. Any misalignment of stream offset, padding, or IV calculation corrupts ciphertext. When `closeOutputStream` is false, `close` does not close the codec either, which may be intentional for shared ownership but can leak codec resources. `setDropBehind` assumes the wrapped stream implements `CanSetDropBehind` and catches only `ClassCastException`. Temporary heap copying can be a performance bottleneck.

## Test Signals

Tests should cover writes across buffer and block boundaries, nonzero initial offset, flush of partial buffers, close with both `closeOutputStream` values, sync delegation, drop-behind unsupported behavior, encryptor context reset handling, IO statistics delegation, and round-trip compatibility with `CryptoInputStream`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoProtocolVersion.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoProtocolVersion.java`

## Purpose

`CryptoProtocolVersion` models versions of the client/server protocol used for HDFS encryption features.

## Important APIs and Types

Enum constants are `UNKNOWN("Unknown",1)` and `ENCRYPTION_ZONES("Encryption zones",2)`. Methods include `supported`, `supports`, `setUnknownValue`, `getUnknownValue`, `getDescription`, `getVersion`, and `toString`.

## Control Flow

`supported` returns the static array currently containing only `ENCRYPTION_ZONES`. `supports` rejects a value with the same version as `UNKNOWN`, then scans all enum values and returns true if any enum constant has the same numeric version.

## State and Persistence

Enum constants store description, numeric version, and mutable `unknownValue`. The static `supported` array is returned directly, so callers can mutate its contents.

## Dependencies and Integration Points

The enum is used in HDFS encryption negotiation and compatibility checks. Numeric versions are wire/protocol values, while descriptions are human-readable.

## Risks

Returning the internal supported array allows accidental modification of global supported versions. `supports` scans all values, not the `supported` array, so future enum constants could be reported supported even if not added to `supported`. `getUnknownValue` can unbox null. `UNKNOWN` and real versions must keep unique numeric IDs.

## Test Signals

Tests should cover supported list contents, `supports` behavior for unknown and real versions, unknown value preservation, mutation risk of returned arrays, and compatibility when adding new protocol versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoProtocolVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoStreamUtils.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoStreamUtils.java`

## Purpose

`CryptoStreamUtils` contains shared helpers for crypto stream buffer management, codec validation, buffer-size normalization, and input stream offset discovery.

## Important APIs and Types

Public static methods are `freeDB(ByteBuffer)`, `getBufferSize(Configuration)`, `checkCodec(CryptoCodec)`, `checkBufferSize(CryptoCodec,int)`, and `getInputStreamOffset(InputStream)`. `MIN_BUFFER_SIZE` is 512.

## Control Flow

`freeDB` uses `CleanerUtil` when unmapping/freeing direct buffers is supported and logs failures. `getBufferSize` reads `hadoop.security.crypto.buffer.size` with its default. `checkCodec` permits only `AES_CTR_NOPADDING` and `SM4_CTR_NOPADDING`. `checkBufferSize` rejects values under 512 and floors the result to a multiple of the cipher block size. `getInputStreamOffset` returns `Seekable.getPos()` when available or zero otherwise.

## State and Persistence

The class is stateless apart from constants and logger. There is no persistence.

## Dependencies and Integration Points

It is used by `CryptoInputStream` and `CryptoOutputStream`. It depends on Hadoop config constants, `CleanerUtil`, `Seekable`, `Preconditions`, and crypto suite metadata.

## Risks

Flooring buffer size can return a value smaller than the configured value; tests should ensure it never drops below useful block multiples after the minimum check. Codec validation must be updated when new CTR-compatible suites are introduced. Direct-buffer freeing is platform/JDK-sensitive and may silently no-op with trace logging.

## Test Signals

Tests should cover minimum buffer rejection, block-size flooring, AES/SM4 acceptance, unsupported suite rejection, seekable and non-seekable offset discovery, and direct-buffer free behavior on supported and unsupported JDKs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoStreamUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoUtils.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoUtils.java`

## Purpose

`CryptoUtils` provides miscellaneous crypto helpers, currently focused on resolving and optionally auto-registering the configured JCE provider.

## Important APIs and Types

The main API is `getJceProvider(Configuration)`. Constants identify the Bouncy Castle provider class and provider name `BC`. Two `LogExactlyOnce` instances prevent repeated warnings.

## Control Flow

`getJceProvider` reads the trimmed provider name and the auto-add flag from configuration. If auto-add is enabled and provider is `BC`, it reflectively loads `org.bouncycastle.jce.provider.BouncyCastleProvider`, constructs it, and calls `Security.addProvider`. Class-load and provider-add failures are logged once. The method returns the configured provider string regardless of whether auto-add succeeded.

## State and Persistence

The utility is final with a private constructor. It has static loggers only. Calling `Security.addProvider` mutates JVM-wide security provider state.

## Dependencies and Integration Points

It depends on Java security provider APIs, Hadoop common crypto configuration keys, `LogExactlyOnce`, and `Configuration`. `JceCtrCryptoCodec` calls it during `setConf`.

## Risks

Provider auto-add uses reflection and can fail due to classpath, constructor, security manager, or provider registration issues. Returning `BC` even when registration failed means later cipher/random initialization may still fail. JVM-global provider mutation can affect unrelated code. Failures are logged once, which reduces noise but can obscure repeated misconfiguration.

## Test Signals

Tests should cover empty provider, non-BC provider, BC with class available/unavailable, auto-add disabled, add-provider exception paths, and interaction with `JceCtrCryptoCodec` cipher and random initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CryptoUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/Decryptor.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/Decryptor.java`

## Purpose

`Decryptor` defines the direct-buffer decryption contract used by Hadoop crypto streams.

## Important APIs and Types

Methods are `init(byte[] key, byte[] iv)`, `isContextReset()`, and `decrypt(ByteBuffer inBuffer, ByteBuffer outBuffer)`. Implementations are private/evolving and typically also share code with encryptors in CTR mode.

## Control Flow

Callers initialize with key and IV before decrypting. Each `decrypt` call consumes bytes from a direct input buffer and writes plaintext to a direct output buffer, advancing positions but not limits. If the implementation reset its internal context, `isContextReset` tells stream wrappers to recalculate IV/padding and reinitialize.

## State and Persistence

The interface owns no state, but implementations generally hold cipher objects and context-reset flags. There is no persistence.

## Dependencies and Integration Points

It is produced by `CryptoCodec.createDecryptor` and consumed by `CryptoInputStream`. It depends on Java `ByteBuffer` and `IOException`.

## Risks

Implementations may not process all input in one call, so callers must be prepared for partial progress. The contract expects direct buffers and positive remaining space, but enforcement is implementation-specific. Incorrect position handling breaks stream offset alignment.

## Test Signals

Tests should verify init failure behavior, full and partial buffer processing, direct-buffer requirements, position advancement, context reset reporting, and compatibility with `CryptoInputStream` padding and seek paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/Decryptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/Encryptor.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/Encryptor.java`

## Purpose

`Encryptor` defines the direct-buffer encryption contract used by Hadoop crypto streams.

## Important APIs and Types

Methods are `init(byte[] key, byte[] iv)`, `isContextReset()`, and `encrypt(ByteBuffer inBuffer, ByteBuffer outBuffer)`. It mirrors the `Decryptor` interface for the encryption direction.

## Control Flow

Callers initialize the encryptor with key and IV, then repeatedly call `encrypt` with direct buffers. The method advances input and output positions and may need multiple calls to process all input depending on implementation. `isContextReset` allows wrappers to detect ciphers that reset internal state and require explicit reinitialization.

## State and Persistence

The interface is stateless, while implementations hold cipher context. There is no persistence beyond ciphertext emitted by stream wrappers.

## Dependencies and Integration Points

It is produced by `CryptoCodec.createEncryptor` and consumed by `CryptoOutputStream`. It depends on Java `ByteBuffer` and `IOException`.

## Risks

Partial processing, non-direct buffers, insufficient output space, and context resets must be handled consistently by stream wrappers and implementations. Incorrect position advancement can corrupt ciphertext alignment.

## Test Signals

Tests should cover init validation, encryption over exact and partial block-size ranges, context reset behavior, buffer position/limit preservation rules, and round-trip decryption with matching `Decryptor`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/Encryptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/JceAesCtrCryptoCodec.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/JceAesCtrCryptoCodec.java`

## Purpose

`JceAesCtrCryptoCodec` is the concrete JCE-backed codec for `AES/CTR/NoPadding`.

## Important APIs and Types

It extends `JceCtrCryptoCodec`, provides a class-specific logger, returns `CipherSuite.AES_CTR_NOPADDING`, delegates IV calculation to the base helper with the AES block size, and creates `JceCtrCipher` instances for encryption and decryption using key algorithm name `AES`.

## Control Flow

When `CryptoCodec` instantiates this class and calls `setConf` through reflection utilities, the base class resolves provider and secure random settings. Stream wrappers call `calculateIV`, `createEncryptor`, and `createDecryptor`. The encryptor/decryptor constructors request JCE ciphers by suite name and optional provider.

## State and Persistence

State is inherited from `JceCtrCryptoCodec`: configuration, provider, and secure random. This subclass adds only a static logger. It persists no data.

## Dependencies and Integration Points

It depends on JCE `Cipher`, `CipherSuite`, and the base `JceCtrCryptoCodec`. It is the default software AES crypto codec used by Hadoop when native or alternate codecs are not selected.

## Risks

Provider misconfiguration or missing AES/CTR support raises `GeneralSecurityException` during encryptor/decryptor creation. The subclass assumes a 16-byte AES block size from the suite. Adding provider-specific behavior must remain compatible with base IV arithmetic.

## Test Signals

Tests should verify suite identity, AES algorithm name, default and configured providers, IV calculation against known vectors, encrypt/decrypt round trips, and factory discovery through `CryptoCodec.getInstance`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/JceAesCtrCryptoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/JceCtrCryptoCodec.java -->
# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/JceCtrCryptoCodec.java`

## Purpose

`JceCtrCryptoCodec` is the abstract JCE implementation base for CTR-mode codecs. It handles provider configuration, secure random creation, IV counter arithmetic, and the shared `JceCtrCipher` implementation that serves as both `Encryptor` and `Decryptor`.

## Important APIs and Types

Public/protected methods include `getProvider`, `calculateIV(byte[],long,byte[],int)`, `close`, `getLogger`, `getConf`, `setConf`, and `generateSecureRandom`. The nested `JceCtrCipher` implements `Encryptor` and `Decryptor` with methods `init`, `encrypt`, `decrypt`, `process`, and `isContextReset`.

## Control Flow

`setConf` stores configuration, resolves the JCE provider through `CryptoUtils.getJceProvider`, reads the secure random algorithm, and creates a provider-specific or default `SecureRandom`, falling back to `new SecureRandom()` on security exceptions. `calculateIV` treats the final eight bytes of the block as a big-endian counter addition over the initial IV, propagating carry through all bytes. `JceCtrCipher` constructs a JCE `Cipher` for the suite and provider, initializes it with a `SecretKeySpec` and `IvParameterSpec`, and processes direct byte buffers through `Cipher.update`. If `update` writes fewer bytes than input size, it calls `doFinal` and marks context reset.

## State and Persistence

The base codec stores `Configuration conf`, `String provider`, and `SecureRandom random`. `JceCtrCipher` stores its JCE cipher, mode, algorithm name, and context-reset flag. There is no persistent state; cipher state is runtime-only.

## Dependencies and Integration Points

It depends on Java JCE, `SecureRandom`, Hadoop `Configuration`, crypto configuration constants, `CryptoUtils`, and `Preconditions`. Concrete subclasses such as `JceAesCtrCryptoCodec` supply suite identity and algorithm name.

## Risks

CTR IV arithmetic is security-critical; counter overflow behavior must match Hadoop's expected wire format. `contextReset` is set false only on `init`, so once a cipher path triggers reset, callers must reinitialize before subsequent use. Provider-specific `Cipher.update(ByteBuffer,ByteBuffer)` behavior may differ, especially around direct buffers and partial output. `close` is a no-op, so provider resources are only JVM-managed. Fallback random creation can silently weaken configured expectations if the requested algorithm/provider fails.

## Test Signals

Tests should cover IV calculation with carry, counter values around block and long boundaries, provider and random algorithm selection/fallback, JCE cipher initialization failures, direct `ByteBuffer` position advancement, context reset path, and concrete codec round trips through `CryptoInputStream`/`CryptoOutputStream`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/JceCtrCryptoCodec.java -->
