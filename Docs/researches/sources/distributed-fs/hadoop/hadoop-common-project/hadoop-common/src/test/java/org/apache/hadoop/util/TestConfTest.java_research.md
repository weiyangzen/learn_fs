<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestConfTest.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestConfTest.java

## Purpose

`TestConfTest.java` tests XML validation performed by `ConfTest.checkConf`.

## Important APIs, Types, and Functions

Each test builds an XML string, wraps it in `ByteArrayInputStream`, calls `ConfTest.checkConf`, and asserts returned error messages. Cases cover empty/valid configs, source duplication, malformed XML, wrong root, wrong child element, missing/empty name/value, duplicated names, and duplicated properties.

## Control Flow

The test flow is table-like: construct input, run validator, assert error list size and exact message content. Valid cases assert an empty error list.

## State and Persistence Behavior

All state is in-memory streams and error lists. No files are used.

## Dependencies and Integration Points

It integrates with the Hadoop configuration XML linting utility and JUnit 5.

## Risks and Edge Cases

Exact line-number messages are sensitive to parser behavior and XML string formatting. Empty values are intentionally valid while empty names are not.

## Test Signals

Signals are exact error strings for structural violations and empty error lists for valid or allowed source duplication cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestConfTest.java -->
