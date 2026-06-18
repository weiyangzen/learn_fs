# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/util/Check.java

## Purpose
`Check` is a small precondition utility for internal HttpFS/lib code. It centralizes argument validation for nulls, empty strings/lists, identifiers, and non-negative/positive numeric values.

## Important APIs, Types, and Functions
Static APIs are `notNull`, `notNullElements`, `notEmpty`, `notEmptyElements`, `validIdentifier`, `gt0(int)`, `gt0(long)`, `ge0(int)`, and `ge0(long)`. `validIdentifier` enforces `[a-zA-Z_][a-zA-Z0-9_\\-]*` and a caller-supplied maximum length.

## Control Flow
Each method validates inputs synchronously and either returns the original value or throws `IllegalArgumentException` with a formatted message. List methods iterate all elements and produce index-specific error text.

## State and Persistence
The class is stateless except for a compiled static `Pattern`. It has no persistence or I/O behavior.

## Dependencies and Integration Points
`ConfigurationUtils` uses `Check.notNull`. Other HttpFS server and service classes use this style to fail fast on invalid configuration or parameters.

## Risks
The methods do not trim strings, so whitespace-only input passes `notEmpty`. Javadoc for `ge0` says "if the integer is greater or equal to zero" in the thrown case, but the implementation correctly rejects negative values. Exceptions expose parameter names and values, which is useful internally but should be considered for externally sourced values.

## Test Signals
No direct tests are in this subset. Indirect coverage comes from components that use these preconditions during HttpFS server setup and parameter handling.
