# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/FastNumberFormat.java

## Purpose

`FastNumberFormat` provides a compact, allocation-light helper for appending a long to a caller-supplied `StringBuilder` with optional zero padding.

## Important APIs, Types, And Functions

The only API is `format(StringBuilder sb, long value, int minimumDigits)`. It handles negative values by appending `-`, computes how many leading zeroes are needed, appends those zeroes, then appends the numeric value.

## Control Flow, State, And Persistence

The method is stateless and thread-safe as long as the caller owns the `StringBuilder`. It uses simple arithmetic rather than `NumberFormat`, so there is no locale or formatter state.

## Dependencies And Integration Points

It has no external dependencies and is suitable for hot paths that need predictable decimal formatting, such as IDs or counters.

## Risks And Test Signals

`Long.MIN_VALUE` remains negative when negated, so tests should verify the expected output for that edge case. Padding behavior should be tested for zero, negative values, minimum digits smaller/larger than actual digits, and builder reuse.
