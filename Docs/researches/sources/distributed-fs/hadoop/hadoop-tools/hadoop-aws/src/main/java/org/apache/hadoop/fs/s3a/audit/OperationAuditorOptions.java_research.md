# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/OperationAuditorOptions.java

## Purpose
`OperationAuditorOptions` is a small builder-style value object used to initialize audit plugins without freezing constructor signatures.

## Important APIs and control flow
`builder()` returns a new mutable options object. `withConfiguration()` and `withIoStatisticsStore()` set fields and return `this`; getters expose both values.

## State, dependencies, and integration
State consists of a Hadoop `Configuration` and an `IOStatisticsStore`. It is created by `ActiveAuditManagerS3A` and passed to `OperationAuditor.init()`.

## Risks and test signals
The builder does not validate missing fields; `AbstractOperationAuditor` requires a non-null statistics store. Tests should verify required fields are set during manager initialization and external auditors remain binary-compatible as options are extended.
