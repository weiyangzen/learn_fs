<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestDelegationTokenAuthenticationHandlerWithMocks.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestDelegationTokenAuthenticationHandlerWithMocks.java

## Purpose
Unit-tests `DelegationTokenAuthenticationHandler` management and authentication behavior with mocked servlet requests/responses and a mocked underlying authentication handler.

## Important APIs, Types, And Functions
Defines `MockDelegationTokenAuthenticationHandler` wrapping an `AuthenticationHandler` that always challenges. Tests target `managementOperation`, `authenticate`, token-manager creation/verification, JSON response generation, `GETDELEGATIONTOKEN`, `RENEWDELEGATIONTOKEN`, and `CANCELDELEGATIONTOKEN`.

## Control Flow
Setup initializes the handler with token kind `foo`. Management-operation tests cover non-management pass-through, wrong HTTP method, unauthenticated management challenges, get-token JSON responses with optional service, missing token parameters, cancel semantics, and renew responses. Authentication tests provide valid/invalid delegation tokens via query string and header. Additional tests ensure a delegation token cannot be used to obtain or renew a token and that JSON mapper configuration can prevent closing the response writer.

## State And Persistence
State is the handler's in-memory token manager and generated tokens. Responses are mocked, with JSON captured in `StringWriter`.

## Dependencies And Integration Points
Depends on servlet APIs, Hadoop auth client/server classes, Jackson `ObjectMapper`, JAX-RS media type constants, Mockito, and UGI. It validates HTTP delegation-token protocol behavior without Jetty or Kerberos.

## Risks
Mocked servlet behavior can miss container-specific query decoding, writer lifecycle, and header casing issues. Some assertions check substrings in JSON or error text. The underlying authentication handler is intentionally minimal.

## Test Signals
Signals include expected HTTP statuses, `WWW-Authenticate` challenge headers, JSON token labels and URL strings, token kind/service values, invalidation after cancel, renewal output containing a long value, valid authentication tokens from query/header inputs, forbidden invalid-token responses, and writer-not-closed behavior under mapper config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/token/delegation/web/TestDelegationTokenAuthenticationHandlerWithMocks.java -->
