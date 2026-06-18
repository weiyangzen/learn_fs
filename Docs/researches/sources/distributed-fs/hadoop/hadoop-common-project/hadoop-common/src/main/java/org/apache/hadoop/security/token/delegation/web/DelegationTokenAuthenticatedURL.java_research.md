<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticatedURL.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticatedURL.java

Source read size: 486 lines, 19328 bytes.

## Purpose
Client-side `AuthenticatedURL` extension that automatically uses Hadoop delegation tokens for HTTP/S connections and exposes helper methods to get, renew, and cancel delegation tokens.

## Important APIs, Types, and Functions
Nested `Token` extends `AuthenticatedURL.Token` with a Hadoop delegation token field. Constructors install a `DelegationTokenAuthenticator` defaulting to `KerberosDelegationTokenAuthenticator`. Important methods are `openConnection()`, `selectDelegationToken()`, `getDelegationToken()`, `renewDelegationToken()`, `cancelDelegationToken()`, `setDefaultDelegationTokenAuthenticator()`, and deprecated `setUseQueryStringForDelegationToken()`.

## Control Flow, State, and Persistence Behavior
When no authenticated cookie token is set, `openConnection()` searches current UGI credentials for a token whose service matches the URL host/port. It sends that token in `X-Hadoop-Delegation-Token` by default or in the `delegation` query parameter for WebHDFS compatibility. Optional `doAs` is appended to the query string. Management helpers delegate to the configured authenticator and keep the nested token's delegation-token field in sync.

## Dependencies and Integration Points
Integrates Hadoop `Credentials`, `SecurityUtil`, `UserGroupInformation`, `AuthenticatedURL`, `DelegationTokenAuthenticator`, and web delegation-token server handlers.

## Risks and Test Signals
Risks include non-thread-safe token state, URL parameter construction that assumes values are already correctly encoded except `doAs`, service matching sensitivity to URL ports, and clearing cached delegation tokens after renewal failures. Test token selection by service, header vs query-string transport, proxy-user parameter, fallback authentication when no token exists, get/renew/cancel flows, and behavior with existing auth cookies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticatedURL.java -->
