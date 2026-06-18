# sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/StsOssClientProviderTest.java

## Purpose
This test verifies STS-backed OSS client initialization and credential refresh.

## Important APIs, Types, And Functions
The test sets OSS endpoint and ECS RAM role configuration, mocks `HttpUtils.get`, injects a mocked `OSSClientBuilder`, calls `init`, manipulates metadata response expiration, and calls `createOrRefreshOssStsClient`.

## Control Flow
Initial metadata returns temporary credentials and should build an OSS client. A later response with a future expiration should refresh credentials, after which `tokenWillExpiredAfter(0)` should be false.

## State And Persistence
State is the provider's in-memory OSS client and expiration timestamp. HTTP responses and client builder are mocked.

## Dependencies And Integration Points
It uses Mockito static mocking for `HttpUtils`, Aliyun OSS client builder, and Alluxio configuration. The provider is used by `OSSUnderFileSystem` when STS mode is enabled.

## Risks
The test uses JSON-like strings with single quotes accepted by Gson leniency; real metadata strictness is not validated. Scheduled background refresh is created by the provider and closed by try-with-resources.

## Test Signals
Passing confirms the provider can parse metadata, build a token client, detect expiring tokens, and refresh credentials.
