# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/StringParam.java

## Purpose
`StringParam` parses and optionally regex-validates string query parameters.

## Important APIs, Types, and Functions
It extends `Param<String>`, stores an optional `Pattern`, and overrides `parseParam` to trim non-null input before parsing. The constructor calls `parseParam(defaultValue)` so defaults are validated. `parse(String)` checks the pattern if present and returns the trimmed string.

## Control Flow
Null, empty, or whitespace-only inputs leave the existing default value unchanged. Nonblank values are trimmed, optionally matched with `Pattern.matches`, and stored as the parsed value. Errors become `IllegalArgumentException` with the pattern or `"a string"` as the domain.

## State and Persistence
State is per parameter instance: pattern plus inherited value.

## Dependencies and Integration Points
Concrete HttpFS parameters use it for paths, users/groups, ACL specs, xattr names/values, snapshot names, storage policy names, and filters. The constructor-time default validation catches invalid defaults at provider instantiation.

## Risks
Blank user input can silently select the default rather than an empty string, which matters for operations where empty strings have semantics. Pattern validation is all-or-nothing and the error does not include the underlying reason.

## Test Signals
`BaseTestHttpFSWith` covers many string parameters, including custom ACL user/group patterns, snapshot names, invalid working directories, invalid xattr names, storage policies, and snapshot diff parameter failures.
