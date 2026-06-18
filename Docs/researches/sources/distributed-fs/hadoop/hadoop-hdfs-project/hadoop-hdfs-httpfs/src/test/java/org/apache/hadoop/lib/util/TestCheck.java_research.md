# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/util/TestCheck.java

Purpose: Unit tests for the `Check` validation utility.

Important APIs/types/functions: `notNull`, `notNullElements`, `notEmptyElements`, `notEmpty`, `validIdentifier`, `gt0`, and `ge0`.

Control flow: positive tests assert valid values are returned unchanged. Negative tests use `assertThrows(IllegalArgumentException.class)` for null values, null/empty collection elements, empty strings, invalid identifiers, too-long identifiers, numeric identifiers, invalid starting characters, zero for `gt0`, and negative values for `gt0`/`ge0`.

State and persistence: none.

Dependencies/integration: `HTestCase`, JUnit assertions, Java collections.

Risks and test signals: broad input-validation guard for shared utility methods used throughout server/config parsing. It does not inspect exception messages, only types.
