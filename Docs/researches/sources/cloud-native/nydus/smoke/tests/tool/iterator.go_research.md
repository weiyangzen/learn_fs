# sources/cloud-native/nydus/smoke/tests/tool/iterator.go

## Purpose
This file implements a small Cartesian-product iterator used to generate dynamic smoke-test scenarios with optional environment and code-based skips.

## Important APIs, Types, And Functions
`DescartesItem` wraps a map of dimension values and exposes `Exists`, `GetString`, `GetBool`, `GetUInt64`, and deterministic `Str`. `DescartesIterator` stores cursors, value lists, dimension-name mapping, optional skip closure, and cached next item. `Dimension` appends a dimension and initializes cursor state. `Skip` registers skip logic. `HasNext`, `Next`, `calNext`, `haveNext`, `noNext`, and `clearNext` drive iteration. `isIgnoredByEnv` implements `SKIP_CASES` filtering of `key=value` pairs.

## Control Flow
The iterator increments cursors like a mixed-radix counter, builds a `DescartesItem`, rejects it if `SKIP_CASES` or the skip closure matches, caches the next valid item, and returns it to generator closures. `Str` sorts keys so subtest names are stable.

## State And Persistence
Iterator state is in memory only. The `SKIP_CASES` environment variable influences scenario selection globally.

## Dependencies And Integration Points
All dynamic test suites use this to produce `test.Generator` cases. It integrates with `tool/test/suite.go`, which executes the generated cases.

## Risks
`isIgnoredByEnv` assumes every comma-separated entry contains `=`, so malformed `SKIP_CASES` can panic. Typed getters use unchecked type assertions. `Dimension` resets `c.cursors[0] = -1`, which works for the intended construction pattern but is fragile if dimensions are manipulated after iteration starts.

## Test Signals
No direct tests are present here. Downstream subtest names and scenario coverage are the visible signals.
