# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/EnumParam.java

## Purpose
`EnumParam` parses a single enum-valued query parameter while accepting lower or mixed case input.

## Important APIs, Types, and Functions
It extends `Param<E>` for `E extends Enum<E>`. The constructor stores the enum `Class<E>`. `parse(String)` uses `Enum.valueOf(klass, StringUtils.toUpperCase(str))`. `getDomain()` returns the comma-joined enum constants.

## Control Flow
The base `Param.parseParam` controls default retention and error wrapping. `EnumParam` transforms input to uppercase before Java enum lookup, matching WebHDFS's case-insensitive operation style.

## State and Persistence
State is per parser instance: the enum class and inherited parsed value.

## Dependencies and Integration Points
It depends on `org.apache.hadoop.util.StringUtils` and is used by concrete HttpFS parameter classes for operation names, xattr encodings, set flags, filesystem actions, and storage-related enum parameters.

## Risks
It only supports enum constants whose canonical name is uppercase-equivalent to the user input. Localized case rules are avoided by Hadoop `StringUtils`, but any enum with nonstandard naming would need a custom parser.

## Test Signals
`BaseTestHttpFSWith` sends many operation names through `HttpFSFileSystem` and WebHDFS clients, indirectly testing enum operation parsing through the server.
