# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/TestKeyProviderDelegationTokenExtension.java

## Purpose
This test verifies delegation-token extension wrapping for key providers, including the default no-token implementation and provider-supplied token behavior.

## Important APIs, Types, and Functions
It uses `KeyProviderDelegationTokenExtension.createKeyProviderDelegationTokenExtension`, `addDelegationTokens`, `DelegationTokenExtension`, `getCanonicalServiceName`, `getDelegationToken`, `Credentials`, and `Token`. `MockKeyProvider` is an abstract test type that extends `KeyProvider` and implements `DelegationTokenExtension`.

## Control Flow
The test first wraps a normal `UserProvider`, calls `addDelegationTokens`, and verifies an empty non-null token array. It then mocks a provider that returns a canonical service name and a token, wraps it, calls `addDelegationTokens("renewer", credentials)`, and verifies the returned token and credentials entry.

## State and Persistence
State is in-memory `Credentials` plus a mocked token with kind `kind` and service `tservice`. No persistent provider data is created.

## Dependencies and Integration Points
Dependencies include `UserProvider`, Hadoop `Credentials`, `Text`, security `Token`, Mockito, and JUnit. The test validates integration between key providers and Hadoop delegation-token collection.

## Risks and Edge Cases
Default providers must not return null token arrays. Providers with canonical service names must store tokens under that canonical service in `Credentials`, not just return them to the caller.

## Test Signals
Passing tests signal correct default extension creation, empty-token behavior, provider extension delegation, token metadata preservation, and credentials insertion.
