# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/LoggingAuditor.java

## Purpose
`LoggingAuditor` is the default audit plugin. It creates spans that log request execution and build an HTTP referrer audit header containing filesystem, user, job, span, path, thread, timestamp, and evaluated audit context fields.

## Important APIs and control flow
The constructor records filesystem ID and current user principal. `serviceInit()` adds job ID when present, reads referrer-header enable/filter settings, creates the `WarningSpan` for outside-span operations, and records whether multipart uploads are enabled. `createSpan()` builds and starts a `LoggingAuditSpan`. In `LoggingAuditSpan.modifyHttpRequest()`, the span may override span ID/operation from AAL execution attributes, attach GET range and delete-key-count attributes, build and store `lastHeader`, append the HTTP referrer header if enabled, debug-log analyzed request details, and reject multipart requests if MPU is disabled. `onExecutionFailure()` maps HTTP status codes to statistics. `WarningSpan` logs outside-span request creation/execution and can throw if rejection is enabled.

## State, dependencies, and integration
State includes global audit attributes, referrer filtering, header enablement, volatile `lastHeader` for tests, warning span, and MPU-enabled flag. Dependencies include AWS SDK request/http/interceptor APIs, Hadoop audit context/referrer builders, user identity, S3A constants, statistics mapping, and `AWSRequestAnalyzer`.

## Risks and test signals
The referrer can expose context unless filters are correct. Header mutation must not break signing, and AAL overrides mutate the span's header builder for that request path. Tests should verify header contents/filtering, disabled-header behavior, `lastHeader`, delete count/range attributes, outside-span rejection policy, multipart-disabled rejection, status-code statistic increments, and AAL span/operation override.
