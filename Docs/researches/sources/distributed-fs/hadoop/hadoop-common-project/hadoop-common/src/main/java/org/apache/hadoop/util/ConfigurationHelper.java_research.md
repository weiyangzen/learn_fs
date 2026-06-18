# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ConfigurationHelper.java

Purpose: `ConfigurationHelper` provides private advanced parsing helpers for configuration enum values beyond the base `Configuration` API.

Important APIs and types: `parseEnumSet`, `mapEnumNamesToValues`, and `resolveEnum`. It defines an error string for case-insensitive enum name collisions.

Control flow: `parseEnumSet` builds a lowercase mapping of enum names, splits a comma-separated value string, treats `*` as all values, adds known values, ignores or rejects unknowns based on `ignoreUnknown`, and returns a mutable `EnumSet`. `mapEnumNamesToValues` detects duplicate lowercase names. `resolveEnum` reads a trimmed configuration value, maps case-insensitively, or calls a fallback function with the raw trimmed value.

State and persistence behavior: stateless; reads from supplied `Configuration`.

Dependencies and integration points: used by private Hadoop code for capability and option parsing; depends on Java `EnumSet`, streams, functions, and Hadoop `StringUtils`.

Risks: duplicate enum names differing only by case fail. `*` plus unknowns can still reject if `ignoreUnknown` is false. Fallback functions must handle empty strings.

Test signals: cover case-insensitive matches, wildcard all, unknown ignored/rejected, duplicate lowercase enum values, prefix mapping, fallback invocation, and empty/null-like config values.
