# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/AuthenticationException.java

Purpose: checked exception representing authentication failures in Hadoop Auth client and server authentication flows.

Important APIs, types, and functions: extends `Exception`, declares `serialVersionUID = 0`, and provides constructors for cause, message, and message plus cause.

Control flow: thrown by authenticators, server handlers, token parsing, and filter logic; callers handle it separately from transport `IOException`.

State and persistence: exception state is the normal Java message/cause chain. No persistent state.

Dependencies and integration points: used throughout client and server packages as the common authentication error type.

Risks and test signals: messages may be propagated to HTTP error reasons by `AuthenticationFilter`, so sensitive details should be avoided. Test signals are exception wrapping paths in Kerberos/Pseudo/filter tests and cause preservation.
