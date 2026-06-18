# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FSBuilderSupport.java

## Purpose
Helper for parsing numeric options from FSBuilder option Configuration with resilient fallback logging.

## Important APIs, Types, and Functions
Constructor/getOptions(); getPositiveLong(); getLong(); static LOG_PARSE_ERROR.

## Control Flow
getLong returns default for empty key, parses with Configuration.getLong, catches NumberFormatException, logs once, and returns default. getPositiveLong additionally replaces negative values with default.

## State and Persistence Behavior
Stores the builder options Configuration. No persistence.

## Dependencies and Integration Points
Used by open/create builder implementations that accept string options.

## Risks and Test Signals
Risks are silent fallback for invalid mandatory-like options and LogExactlyOnce suppressing repeated diagnostics. Tests should cover empty, valid, invalid, and negative values.
