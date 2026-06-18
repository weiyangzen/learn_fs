# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DtFetcher.java

## Purpose

`DtFetcher` is the ServiceLoader extension interface used by `dtutil` to fetch delegation tokens from service-specific implementations at runtime.

## Important APIs, Types, and Functions

It declares `getServiceName`, `isTokenRequired`, and `addDelegationTokens(Configuration, Credentials, String renewer, String url)`.

## Control Flow

`DtFileOperations.getTokenFile` discovers implementations, matches service name against URL scheme or explicit service option, verifies a token is required, and delegates token addition to the matching fetcher.

## State and Persistence Behavior

The interface owns no state. Implementations mutate the supplied `Credentials` and may return a token suitable for aliasing.

## Dependencies and Integration Points

It depends on `Configuration`, `Credentials`, `Text`, and `Token`. Implementations are loaded through Java `ServiceLoader`.

## Risks and Edge Cases

Multiple fetchers can match the same service. `isTokenRequired` false is treated as an error in dtutil get. Returning null prevents aliasing.

## Test Signals

Tests should cover ServiceLoader discovery, service matching, no-token-required errors, null returned token with alias, and successful credentials mutation.
