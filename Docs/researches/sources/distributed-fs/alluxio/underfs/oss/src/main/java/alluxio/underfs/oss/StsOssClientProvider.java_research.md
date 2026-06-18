# sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/StsOssClientProvider.java

## Purpose
`StsOssClientProvider` manages an Aliyun OSS client backed by temporary STS credentials fetched from ECS RAM role metadata.

## Important APIs, Types, And Functions
The public APIs are constructor, `init`, `createOrRefreshOssStsClient`, `getOSSClient`, and `close`. Internals include `tokenWillExpiredAfter`, `doCreateOrRefreshStsOssClient`, `convertStringToDate`, and `setOssClientBuilder` for tests.

## Control Flow
Construction stores configuration and schedules a refresh task every 60 seconds. `init` retries client creation with exponential backoff. Refresh fetches metadata JSON from the ECS metadata service plus role name, parses access key, secret, token, and expiration, then either builds the OSS client or switches credentials on the existing client.

## State And Persistence
State includes a volatile OSS client, token expiration timestamp, metadata URL, token refresh interval, scheduled executor, and client builder. No credentials are persisted to disk.

## Dependencies And Integration Points
It depends on `HttpUtils`, Gson, OSS SDK credential switching, Alluxio retry utilities, and `OSSUnderFileSystem.initializeOSSClientConfig`.

## Risks
Metadata response parsing assumes all fields are present and valid. Scheduled refresh starts in the constructor, so lifecycle must call `close`. Time-based refresh can serve expired credentials if metadata fetch repeatedly fails.

## Test Signals
`StsOssClientProviderTest` mocks metadata HTTP responses and `OSSClientBuilder` to validate initial client creation and refresh when token expiration approaches.
