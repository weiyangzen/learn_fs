<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/PseudoDelegationTokenAuthenticator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/PseudoDelegationTokenAuthenticator.java

Source read size: 54 lines, 2018 bytes.

## Purpose
Client-side delegation-token authenticator for Hadoop simple/pseudo HTTP authentication.

## Important APIs, Types, and Functions
Extends `DelegationTokenAuthenticator` and constructs it with a `PseudoAuthenticator`.

## Control Flow, State, and Persistence Behavior
All operational flow is inherited. Without a delegation token it authenticates using the pseudo authenticator, typically by sending the user name expected by Hadoop Auth; with a token it bypasses normal auth and uses the token header or query parameter.

## Dependencies and Integration Points
Pairs with `PseudoDelegationTokenAuthenticationHandler` and can be installed in `DelegationTokenAuthenticatedURL` where simple auth is desired.

## Risks and Test Signals
Risks are inherited from pseudo authentication and delegation-token URL construction. Test pseudo-auth token acquisition, delegation-token bypass on subsequent requests, renew and cancel calls, doAs handling, and failure propagation from non-200 or non-JSON server responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/PseudoDelegationTokenAuthenticator.java -->
