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
