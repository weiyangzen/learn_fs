# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/impl/ReferrerExtractor.java

## Purpose

`ReferrerExtractor.java` is a tiny test-only helper that exposes `LoggingAuditor.getReferrer()` behavior to tests despite package/private span wrapping details.

## Important APIs, Types, and Functions

The class has a private constructor and one static method, `getReferrer(LoggingAuditor auditor, AuditSpanS3A span)`, returning `HttpReferrerAuditHeader`.

## Control Flow

The helper checks whether the supplied span is an `ActiveAuditManagerS3A.WrappingAuditSpan`; if so, it unwraps to the inner span before delegating to `auditor.getReferrer()`. Otherwise it passes the span through directly.

## State and Persistence Behavior

The class is stateless. It only exposes existing span/auditor state.

## Dependencies and Integration Points

It integrates tests in the public audit package with implementation classes in `audit.impl`, especially logging-auditor referrer generation and active-manager wrapping.

## Risks and Edge Cases

Passing a span from a different auditor implementation can raise `ClassCastException`, as documented. This is acceptable because it is a narrow test helper.

## Test Signals

The main signal is `TestHttpReferrerAuditHeader.testSpanResilience()`, which obtains a referrer from a wrapped logging span and verifies failure-resilient header building.
