<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration.cc

## Purpose
Implements the immutable `Configuration` value object used to store Hadoop XML properties and retrieve them as strings, integers, doubles, booleans, and URIs.

## Important APIs, Types, And Functions
`GetDefaultFilenames()` returns `core-site.xml`. `Get`, `GetWithDefault`, `GetInt`, `GetDouble`, `GetBool`, `GetUri`, and their default variants read from `raw_values_`. `fixCase()` uppercases keys so lookups are case-insensitive.

## Control Flow
Each getter normalizes the key, looks in the parsed map, and converts the raw string if needed. Numeric getters use `strtol`/`strtod`, boolean accepts case-insensitive `true`/`false`, and URI parsing catches `uri_parse_error` and returns empty optional on failure.

## State And Persistence
State is a copyable `ConfigMap` of uppercase key to `ConfigData {value, final}`. Once constructed by `ConfigurationLoader`, callers only read it; no durable writes occur.

## Dependencies And Integration Points
The class depends on `URI`, the optional wrapper, and x-platform case-insensitive comparison. `HdfsConfiguration` subclasses it to interpret HDFS-specific keys.

## Risks
Numeric parsing does not require the whole string to be consumed, so values with numeric prefixes may be accepted. `fixCase()` calls `toupper` on `char`, which can be locale/negative-char sensitive. Unsupported Hadoop config features are explicitly noted: substitutions, ranges, byte/time units, string lists, and deprecated values.

## Test Signals
Tests should cover case-insensitive lookup, missing values, invalid and range-overflow numerics, booleans, URI errors, default handling, `final` propagation through loader-created maps, and thread-safe sharing of copied configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration.cc -->
