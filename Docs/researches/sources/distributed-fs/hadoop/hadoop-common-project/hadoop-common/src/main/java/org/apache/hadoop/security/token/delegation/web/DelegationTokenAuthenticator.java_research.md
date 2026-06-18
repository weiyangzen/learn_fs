<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticator.java

Source read size: 358 lines, 14344 bytes.

## Purpose
Client-side `Authenticator` wrapper that skips normal HTTP authentication when a delegation token is present and implements REST operations for obtaining, renewing, and canceling delegation tokens.

## Important APIs, Types, and Functions
Important constants define query/header names and JSON fields: `op`, `delegation`, `token`, `renewer`, `service`, `X-Hadoop-Delegation-Token`, `Token`, `urlString`, and `long`. The `DelegationTokenOperation` enum maps operations to HTTP methods and whether Kerberos credentials are required. Public methods are `authenticate()`, `getDelegationToken()`, `renewDelegationToken()`, `cancelDelegationToken()`, and `setConnectionConfigurator()`.

## Control Flow, State, and Persistence Behavior
`authenticate()` detects a delegation token either in the nested URL token object or in the query string. Without one it checks/relogs in the current UGI TGT and delegates to the wrapped authenticator. Management operations build a URL with encoded parameters, temporarily clear delegation token state when real credentials are required, open an `AuthenticatedURL`, set the required method, validate HTTP 200, and parse JSON if a response is expected. No persistent state is owned beyond the wrapped authenticator/configurator references.

## Dependencies and Integration Points
Wraps Hadoop Auth client authenticators, normally Kerberos or pseudo. Integrates with `DelegationTokenAuthenticatedURL`, `SecurityUtil`, `JsonSerialization`, `HttpExceptionUtils`, and the server handler's REST contract.

## Risks and Test Signals
Risks include substring-based query detection for `delegation=`, unchecked JSON casts, URL assembly with parameter order from `HashMap`, clearing/restoring token state around Kerberos-required ops, and cancellation converting unexpected auth exceptions to IOExceptions. Test each operation URL/method, JSON content-type validation, non-JSON response, delegation-token bypass, TGT relogin path, doAs encoding, and restoration of token state after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/DelegationTokenAuthenticator.java -->
