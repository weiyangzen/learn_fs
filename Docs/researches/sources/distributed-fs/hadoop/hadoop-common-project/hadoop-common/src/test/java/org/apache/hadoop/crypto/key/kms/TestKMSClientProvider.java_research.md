# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/kms/TestKMSClientProvider.java

## Purpose
`TestKMSClientProvider` validates delegation-token service selection for a single KMS client, including the newer full provider-URI token service and legacy `host:port` token service.

## Important APIs, Types, and Functions
It exercises `KMSClientProvider.selectDelegationToken(Credentials, Text)`, instance `selectDelegationToken(Credentials)`, `createAuthenticatedURL()`, and `DelegationTokenAuthenticatedURL.selectDelegationToken(URL, Credentials)`. Tokens use `KMSDelegationToken.TOKEN_KIND`.

## Control Flow
`setup()` disables IP-based token services and initializes one token with service `kms://https@host:16000/kms` and one legacy token with service `host:16000`. Tests verify static selection only matches requested service, instance selection accepts legacy service when appropriate, newer URI-format tokens win when both exist, and authenticated URLs can select either service format.

## State and Persistence
State is in-memory credentials and tokens. Each provider is closed in `finally` blocks where instantiated.

## Dependencies and Integration Points
Dependencies include `KMSClientProvider`, `KMSDelegationToken`, Hadoop `Credentials`, `SecurityUtil`, `DelegationTokenAuthenticatedURL`, Java `URI`/`URL`, and JUnit.

## Risks and Edge Cases
Backward compatibility with legacy token service names is critical for existing clients. The newer URI service must take precedence when both tokens exist to avoid selecting stale or less-specific credentials.

## Test Signals
Passing tests signal correct KMS token lookup by service text, legacy fallback, new-format precedence, and authenticated URL token selection.
