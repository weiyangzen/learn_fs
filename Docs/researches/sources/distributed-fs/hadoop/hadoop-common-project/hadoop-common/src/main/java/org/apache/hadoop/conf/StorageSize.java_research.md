# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/StorageSize.java`

## Purpose

`StorageSize` pairs a numeric double value with a `StorageUnit` and parses human-readable storage size strings used by `Configuration.getStorageSize`.

## Important APIs and Types

The constructor stores `StorageUnit unit` and `double value`. Public methods are static `parse(String)`, `getUnit`, and `getValue`.

## Control Flow

`parse` rejects blank input, lowercases and trims it, then scans `StorageUnit.values()` for a suffix match against long name, short name, or single-character suffix. It then chooses the longest suffix match in long-name, short-name, suffix-character order, strips that suffix, parses the remaining numeric part as a `double`, and returns a new `StorageSize`.

## State and Persistence

Instances are immutable: both fields are final and no setters exist. No persistence is implemented.

## Dependencies and Integration Points

It depends on `StorageUnit`, `Locale.ENGLISH`, and Apache Commons `isNotBlank`. It is called by `Configuration` storage-size getters to parse strings like `100MB` before converting to target units.

## Risks

The initial unit scan relies on `StorageUnit` declaration order, especially because bytes uses the short name/suffix `b` and can match many longer suffixes if ordered incorrectly. The substring uses the original input length rather than the sanitized length, which is fine for same-length trim/lowercase content after trim but should be protected by tests around leading/trailing whitespace. The parser accepts any `Double.parseDouble` format after suffix stripping, including negative and special values if Java accepts them.

## Test Signals

Tests should cover long, short, and one-character suffixes for every unit; case and whitespace normalization; invalid or missing suffixes; decimal values; byte suffix ambiguity; and integration with `Configuration.getStorageSize`.
