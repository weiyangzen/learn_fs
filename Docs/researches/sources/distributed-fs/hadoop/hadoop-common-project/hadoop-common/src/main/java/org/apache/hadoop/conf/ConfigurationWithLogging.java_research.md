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
