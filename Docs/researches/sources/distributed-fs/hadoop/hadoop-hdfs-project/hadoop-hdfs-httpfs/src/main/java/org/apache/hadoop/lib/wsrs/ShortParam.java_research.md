# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/ShortParam.java

## Purpose
`ShortParam` parses short integer query parameters, optionally in a caller-supplied radix.

## Important APIs, Types, and Functions
It extends `Param<Short>`. Constructors accept name/default/radix or name/default with radix 10. `parse(String)` calls `Short.parseShort(str, radix)`. `getDomain()` reports `"a short"`.

## Control Flow
Base default handling is used. Nonblank strings are parsed under the configured radix.

## State and Persistence
Each instance stores its radix and inherited parsed value. No persistence or I/O occurs.

## Dependencies and Integration Points
HttpFS parameter definitions use short values for HDFS settings such as replication and octal permissions when concrete subclasses choose the appropriate radix.

## Risks
The validation message does not mention radix, so octal/decimal failures may be unclear. No semantic range beyond Java `short` is enforced.

## Test Signals
`BaseTestHttpFSWith` exercises replication and permissions through create, setReplication, and setPermission operations, indirectly covering short-valued parameter parsing.
