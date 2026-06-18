# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/Authenticator.java

Purpose: client-side authentication mechanism contract for `AuthenticatedURL`.

Important APIs, types, and functions: declares `setConnectionConfigurator(ConnectionConfigurator)` and `authenticate(URL, AuthenticatedURL.Token)`.

Control flow: `AuthenticatedURL.openConnection()` calls `authenticate()` before opening the caller's connection. Implementations may no-op when the token is already set, perform SPNEGO, pseudo auth, or custom flows, and update the token on success.

State and persistence: interface has no state. Implementations are documented as use-once and need not be thread-safe.

Dependencies and integration points: implemented by `KerberosAuthenticator` and `PseudoAuthenticator`, and extensible for custom client auth. It integrates with URL connections and the token cookie abstraction.

Risks and test signals: implementations must consistently use the supplied `ConnectionConfigurator`; otherwise TLS/proxy settings may be lost. Test signals are custom authenticator injection and configured connection behavior.
