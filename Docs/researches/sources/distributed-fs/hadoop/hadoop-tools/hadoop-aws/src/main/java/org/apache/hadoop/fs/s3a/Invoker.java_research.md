# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Invoker.java

Purpose: central lambda-based invocation wrapper for S3A operations, providing one-shot exception translation, retry loops, future awaiting, quiet/ignored execution, duration tracking, and retry callbacks.

Important APIs/types: constructor takes Hadoop `RetryPolicy` and default `Retried` callback. Static methods include `once`, `onceTrackingDuration`, `onceInTheFuture`, `ignoreIOExceptions`, `quietly`, and `quietlyEval`. Instance methods include `retry`, `maybeRetry`, and `retryUntranslated` variants. Nested `Retried` functional interface reports retry events; `NO_OP` and `LOG_EVENT` are default callbacks. Methods are annotated with source-retained `Retries` annotations documenting translation/retry contracts.

Control flow: one-shot methods execute operations and translate `SdkException` through `S3AUtils.translateException`. Retry methods wrap one-shot execution or raw operations, then call `retryPolicy.shouldRetry` with translated IOExceptions, idempotency, and retry count. On retry, callback is invoked before sleeping. Interrupted sleeps become `InterruptedIOException` and re-interrupt the thread. If the retry policy itself fails, the original caught exception is rethrown.

State and persistence behavior: immutable retry policy and callback references. No persistent state. Per-call retry count and caught exception are local.

Dependencies and integration points: integrates S3A operations with Hadoop retry policy, AWS SDK exceptions, S3A exception translation, IO statistics duration tracking, `FutureIO`, and logging. It is used broadly around object-store calls.

Risks: idempotency flag correctness is critical; marking a non-idempotent operation idempotent can duplicate side effects. `retryUntranslated` translates SDK exceptions only for policy decisions and may rethrow the raw SDK exception after retries. Sleep delays block the invoking thread.

Test signals: tests should cover one-shot translation, future exception translation, retry count/delay/callback behavior, idempotent vs non-idempotent policy decisions, interrupt handling, quiet optional behavior, and no nested retry misuse for methods already annotated as retried.
