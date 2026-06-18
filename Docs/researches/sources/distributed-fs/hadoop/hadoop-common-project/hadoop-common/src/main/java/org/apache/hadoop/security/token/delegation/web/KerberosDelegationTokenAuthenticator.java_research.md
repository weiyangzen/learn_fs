<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/KerberosDelegationTokenAuthenticator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/KerberosDelegationTokenAuthenticator.java

Source read size: 46 lines, 1852 bytes.

## Purpose
Client-side delegation-token authenticator for Kerberos/SPNEGO-backed Hadoop HTTP endpoints.

## Important APIs, Types, and Functions
Extends `DelegationTokenAuthenticator` and constructs it with a `KerberosAuthenticator`.

## Control Flow, State, and Persistence Behavior
All behavior is inherited from `DelegationTokenAuthenticator`: perform SPNEGO only when no delegation token is present, and use Kerberos credentials for get/renew operations. The class owns no additional state.

## Dependencies and Integration Points
Used as the default authenticator by `DelegationTokenAuthenticatedURL`. Integrates with Hadoop Auth `KerberosAuthenticator` and server-side `KerberosDelegationTokenAuthenticationHandler`.

## Risks and Test Signals
Risks are inherited from the generic authenticator plus Kerberos environment sensitivity. Test default authenticator instantiation, SPNEGO handshake on token acquisition, no-handshake data requests when a token exists, renew requiring credentials, cancel not requiring credentials, and propagation of Kerberos IO/auth failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/KerberosDelegationTokenAuthenticator.java -->
