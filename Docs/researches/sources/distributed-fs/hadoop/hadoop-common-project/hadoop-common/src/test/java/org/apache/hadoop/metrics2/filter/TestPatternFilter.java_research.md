# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/filter/TestPatternFilter.java

## Purpose

`TestPatternFilter` validates common include/exclude semantics shared by metrics glob and regex filters for names, tags, and complete metrics records.

## Important APIs, Types, And Functions

The file uses `GlobFilter`, `RegexFilter`, `MetricsFilter.accepts(...)`, `ConfigBuilder`, `SubsetConfiguration`, `MetricsTag`, and mocked `MetricsRecord`. Public helpers `newGlobFilter()` and `newRegexFilter()` are reused by other metrics tests.

## Control Flow

Tests build filter configs with `include`, `include.tags`, `exclude`, and `exclude.tags`, then call helper assertions against strings, tag lists, and mock records. Cases cover empty config accepting everything, include-only whitelisting, exclude-only blacklisting, combined include/exclude accepting unmatched items while rejecting excluded matches, and include patterns overriding identical excludes. Per-tag assertions ensure list-level acceptance and individual tag decisions line up for both glob and regex filters.

## State And Persistence Behavior

State is only in the constructed `PropertiesConfiguration`/`SubsetConfiguration` and initialized filter objects. No persistence is involved.

## Dependencies And Integration Points

The test integrates with metrics2 filter implementations, config utilities, interned metric tags, and Mockito. Other tests import its filter factory helpers for collector filtering.

## Risks And Test Signals

Risks include glob/regex semantic divergence, wrong precedence between include and exclude, rejecting unmatched items when both filters are configured, and incorrect tag-list aggregation. Signals compare both filter types on every case and assert both aggregate list result and individual tag result.
