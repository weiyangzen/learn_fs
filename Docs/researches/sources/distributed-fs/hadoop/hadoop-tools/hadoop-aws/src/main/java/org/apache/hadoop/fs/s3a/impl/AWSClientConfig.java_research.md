# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/AWSClientConfig.java

## Purpose
Central builder utilities for AWS SDK v2 client configuration in S3A. It configures request timeouts, user agent, custom headers, signer overrides, retry policy, sync/async HTTP clients, proxy settings, and per-request timeout overrides.

## Important APIs, Types, And Functions
`createClientConfigBuilder()` initializes `ClientOverrideConfiguration`. `createHttpClientBuilder()` configures Apache HTTP; `createAsyncHttpClientBuilder()` configures Netty async HTTP. `createRetryPolicyBuilder()` uses adaptive retry mode. `createProxyConfiguration()` and `createAsyncProxyConfiguration()` build sync/async proxy config with credential validation. `createApiConnectionSettings()` and `createConnectionSettings()` derive validated timeout settings. `setRequestTimeout()` patches individual AWS requests.

## Control Flow
Client config creation applies request timeout, user agent, custom service headers, generic signer override, then service-specific signer override. HTTP client creation reads common connection settings and maps them onto Apache or Netty builders. Proxy creation handles host/port/default-port combinations and rejects username/password mismatches or port-without-host.

## State And Persistence
Only mutable static state is `minimumOperationDuration`, test-adjustable and resettable. All builders are runtime configuration objects; no persistent state.

## Dependencies And Integration Points
Used by S3A client factories and AWS service clients. Depends on Hadoop `Configuration`, S3A constants, `S3AUtils`, `SignerFactory`, `NetworkBinding`, AWS SDK v2 client/http/retry APIs, and Hadoop `VersionInfo`.

## Risks
Timeout minimums can affect production latency if test overrides leak. Proxy logging at debug includes password values. Service-specific signer overrides supersede generic signer settings. Async proxy lacks NTLM support noted by TODO.

## Test Signals
Cover timeout minimum enforcement/reset, sync and async builder mappings, retry count bounds, proxy host/port/default behavior, credential mismatch failures, custom header parsing, generic and service-specific signer precedence, user-agent prefix, and per-request timeout override.
