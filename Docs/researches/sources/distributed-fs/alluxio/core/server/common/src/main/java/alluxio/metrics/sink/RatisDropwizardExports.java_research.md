# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/RatisDropwizardExports.java

## Purpose
`RatisDropwizardExports` adapts Dropwizard metrics for Prometheus while applying Ratis-specific name rewriting.

## Important APIs, Types, and Functions
It extends `DropwizardExports`, constructs with `RatisNameRewriteSampleBuilder`, and exposes `registerRatisMetricReporters(Map<String, RatisDropwizardExports>)`. Private helpers `registerDropwizard()` and `deregisterDropwizard()` register/unregister collectors as Ratis metric registries appear or disappear.

## Control Flow, State, and Persistence
`registerRatisMetricReporters()` installs callbacks into `MetricRegistries.global()`. On registration, it wraps a Ratis Dropwizard registry, registers the collector in Prometheus' default registry, and records it by registry name. On deregistration, it removes the collector from the map and unregisters it if present.

## Dependencies and Integration Points
It depends on Apache Ratis metric registries, Prometheus collector registry, Dropwizard exports, and `RatisNameRewriteSampleBuilder`. It bridges Ratis embedded journal metrics into Alluxio's Prometheus endpoint.

## Risks and Test Signals
Risks include duplicate collector registration, deregistration races, and map thread-safety depending on caller-provided map. Signals are Ratis metrics appearing with rewritten labels, successful unregister on registry removal, and no default-registry collisions.
