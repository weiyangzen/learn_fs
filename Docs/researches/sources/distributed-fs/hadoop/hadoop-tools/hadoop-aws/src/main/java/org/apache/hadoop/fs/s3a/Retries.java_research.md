# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Retries.java

Purpose: package-private documentation annotations describing whether S3A methods perform retrying and/or exception translation internally.

Important APIs/types: final-ish utility class with nested source-retention annotations: `OnceTranslated`, `OnceRaw`, `OnceMixed`, `RetryTranslated`, `RetryRaw`, `RetryMixed`, `RetryExceptionsSwallowed`, and `OnceExceptionsSwallowed`.

Control flow: no runtime behavior. Annotations are retained only in source and used to guide maintainers/callers.

State and persistence behavior: none.

Dependencies and integration points: complements Hadoop retry annotations like `Idempotent` but is not an RPC marker. Used throughout S3A methods such as `Invoker` and listing utilities to avoid nested retries or double translation.

Risks: because retention is source-only, tooling and runtime checks cannot enforce the contract. Documentation can drift from implementation.

Test signals: no direct runtime tests; code review and static source checks can verify retry-sensitive APIs are annotated consistently.
