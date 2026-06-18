# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRetryCache.java

Purpose: tests `RetryCache` behavior for idempotent server operations under concurrent retries, covering success/failure and long/short operation timing.

Important APIs/types/functions: `RetryCache`, `RetryCache.CacheEntryWithPayload`, `RetryCache.waitForCompletion()`, `RetryCache.setState()`, `Server.Call`, `Server.getCurCall()`, `ClientId.getClientId()`, and local `TestServer.echo()`.

Control flow: `newCall()` creates a synthetic call with stable client ID and call ID. `TestServer.echo()` waits for/creates a retry cache entry, returns cached payload for successful completed entries, otherwise increments operation count, optionally sleeps, sets cache state, and returns success or failure output. `testOperations()` starts many threads sharing the same current call and asserts all return expected values plus operation/retry counters.

State and persistence behavior: retry cache state is in-memory with a long expiration period; call identity comes from thread-local current calls. Static `callId`, `CLIENT_ID`, random, and shared `TestServer` persist across tests, while counters reset before each test.

Dependencies and integration points: models how Hadoop RPC servers deduplicate retried idempotent operations by `(clientId, callId)`, and how failed operations are not reused as successful payloads.

Risks and test signals: strong concurrency signal that only one successful operation executes and all other attempts reuse payload, while failed attempts execute independently. Some test names/comments around short success appear inconsistent with the `success` argument, so readers should trust assertions over comments.
