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
