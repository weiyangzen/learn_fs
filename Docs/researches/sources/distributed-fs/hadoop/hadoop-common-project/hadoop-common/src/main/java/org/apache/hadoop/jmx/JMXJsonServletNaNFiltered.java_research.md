<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/JMXJsonServletNaNFiltered.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/JMXJsonServletNaNFiltered.java

## Purpose
`JMXJsonServletNaNFiltered` customizes `JMXJsonServlet` to serialize values whose string form is `NaN` as numeric `0.0`, avoiding invalid JSON number output.

## Important APIs, Types, And Functions
- Overrides `extraCheck(Object value)` to return true when `Objects.toString(value).trim()` equals `NaN`.
- Overrides `extraWrite(...)` to log and write `0.0`.

## Control Flow
During `JMXJsonServlet.writeObject`, subclass `extraCheck` runs before generic `Number` handling. Matching values are passed to `extraWrite`, which writes a replacement numeric value.

## State And Persistence
Stateless except for logging. No persistence.

## Dependencies And Integration Points
Depends on the base servlet extension hooks, Jackson `JsonGenerator`, and SLF4J. Intended for Hadoop web endpoints whose metrics wrappers may produce NaN-like values without implementing `Number`.

## Risks And Edge Cases
Any object whose trimmed string is exactly `NaN` is coerced to `0.0`, which preserves JSON validity but may hide missing/undefined metric semantics. Case variants such as `nan` are not matched.

## Test Signals
Tests should verify string-like and wrapper NaN values become `0.0`, normal numbers still serialize normally, and recursive array/composite paths apply the filter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/jmx/JMXJsonServletNaNFiltered.java -->
