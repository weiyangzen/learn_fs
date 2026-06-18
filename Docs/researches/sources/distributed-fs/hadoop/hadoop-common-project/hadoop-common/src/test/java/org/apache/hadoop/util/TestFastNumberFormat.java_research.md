<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestFastNumberFormat.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestFastNumberFormat.java

## Purpose

`TestFastNumberFormat.java` validates padded integer formatting against Java `NumberFormat`.

## Important APIs, Types, and Functions

It tests `FastNumberFormat.format(StringBuilder, long, minDigits)` for positive, zero, and negative long values with `MIN_DIGITS = 6`.

## Control Flow

The test configures a no-grouping `NumberFormat` with six minimum integer digits, formats a list of values through both implementations, and compares strings.

## State and Persistence Behavior

State is local formatter/string builder data only. No persistence exists.

## Dependencies and Integration Points

It integrates with `FastNumberFormat`, Java `NumberFormat`, JUnit 5, and a one-second timeout.

## Risks and Edge Cases

Negative values, zero, and values wider than the minimum width are the main edge cases. Locale-dependent `NumberFormat` behavior could matter if digits are non-ASCII in a locale.

## Test Signals

The exact string equality to `NumberFormat` for all sample values is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestFastNumberFormat.java -->
