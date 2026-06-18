# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/RatisNameRewriteSampleBuilder.java

## Purpose
`RatisNameRewriteSampleBuilder` rewrites Ratis Dropwizard metric names into Prometheus samples with explicit `instance`, `group`, and `follower` labels.

## Important APIs, Types, and Functions
It extends `DefaultSampleBuilder`, overrides `createSample()`, and defines `normalizeRatisMetric(String, List<String>, List<String>)`. It keeps regex patterns for follower-related metric names.

## Control Flow, State, and Persistence
For metric names starting with Ratis' application metrics prefix, `createSample()` copies the existing label lists, normalizes the name, appends labels, optionally logs trace output, and delegates to the parent. Non-Ratis names are passed through. Normalization splits names by `.`, extracts the third segment as `instance` and optional `group` separated by `@`, removes that segment, then matches follower-id patterns in the new third segment and converts follower ids into labels.

## Dependencies and Integration Points
It depends on Ratis metric naming constants, Prometheus Dropwizard sample builder APIs, regexes, and Log4j `Strings.join`. It is used by `RatisDropwizardExports`.

## Risks and Test Signals
Risks include regex overmatching, label cardinality from follower ids, unexpected metric name shapes, and mutation assumptions around label lists. Signals are representative Ratis metric names yielding stable sample names and labels, pass-through for non-Ratis metrics, and trace logs for rewritten metrics.
