# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/AuditTestSupport.java

## Purpose

`AuditTestSupport.java` centralizes test helpers for S3A auditing configuration, statistics, and assumptions.

## Important APIs, Types, and Functions

It exposes `NOOP_SPAN`, `noopAuditor()`, `noopAuditConfig()`, `loggingAuditConfig()`, `enableLoggingAuditor()`, `createIOStatisticsStoreForAuditing()`, `resetAuditOptions()`, and `requireOutOfSpanOperationsRejected()`.

## Control Flow

Configuration helpers construct or patch `Configuration` objects with audit service class names, enable flags, and out-of-span rejection. Statistics helper builds an `IOStatisticsStore` with audit and HTTP response counters. `requireOutOfSpanOperationsRejected()` skips tests if the filesystem audit manager is configured not to reject out-of-span calls.

## State and Persistence Behavior

The class has no instance state. It creates fresh configurations and stores, and mutates configurations passed to reset/enable methods.

## Dependencies and Integration Points

It integrates with `NoopAuditManagerS3A`, `NoopAuditor`, S3A audit constants, `S3ATestUtils.removeBaseAndBucketOverrides()`, IOStatistics binding, and AssertJ assumptions.

## Risks and Edge Cases

Reset coverage must stay aligned with audit options; omitted options can leak bucket-specific settings into tests. The no-op span is reusable and intentionally shared.

## Test Signals

Signals are consistent audit configs, wired statistics counters, and accurate skip behavior for out-of-span rejection dependent tests.
