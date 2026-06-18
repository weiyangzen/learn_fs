# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/impl/ActiveAuditManagerS3A.java

## Purpose
`ActiveAuditManagerS3A` is the active audit manager service. It creates the configured auditor, wraps auditor spans, tracks the active span per thread, attaches spans to AWS SDK execution attributes, and forwards SDK interceptor callbacks to the correct span.

## Important APIs and control flow
Lifecycle: `serviceInit()` builds `OperationAuditorOptions`, creates the configured auditor, and adds it as a child service. `serviceStart()` wraps the auditor's unbonded span. `createSpan()` requires the manager to be started, increments the audit span creation statistic, asks the auditor for a span, wraps it, and makes it current for the thread. `createExecutionInterceptors()` returns this manager plus any configured v2 interceptors, warning about deprecated v1 handlers. `beforeExecution()` increments request execution statistics, attaches the active span to `ExecutionAttributes`, and delegates. Later callbacks call `extractAndActivateSpanFromRequest()` to recover the attached span, switch thread context if it is a wrapper, and delegate to the span. `WrappingAuditSpan` forwards all AWS callbacks to the inner span and removes/prunes thread-map entries on deactivation.

## State, dependencies, and integration
State includes the configured `OperationAuditor`, `AWSRequestAnalyzer`, unbonded wrapper span, `WeakReferenceThreadMap`, prune countdown, and `IOStatisticsStore`. It integrates with AWS SDK `ExecutionInterceptor`, transfer-manager listeners, S3A statistics, audit constants, and configured external interceptors.

## Risks and test signals
Weak-reference tracking can lose spans if callers drop references early; `noteSpanReferenceLost()` is the signal. Missing or non-wrapper execution attributes fall back to thread span and log warnings. Tests should cover lifecycle ordering, span attach/retrieve across every interceptor callback, transfer listener context restoration, pruning, configured interceptor construction, audit failure counter increments, and disabled/deprecated handler behavior.
