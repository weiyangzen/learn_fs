# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/KerberosAuthenticator.java

Purpose: client-side Kerberos SPNEGO authenticator for Hadoop Auth. It uses the current subject or OS ticket cache and falls back to pseudo authentication when the endpoint does not start a SPNEGO negotiation.

Important APIs, types, and functions: constants mirror HTTP auth headers and `Negotiate`; auth probe method is `OPTIONS`. Nested `KerberosConfiguration` builds JAAS entries for OS login and Kerberos ticket cache, with IBM Java and `KRB5CCNAME` handling. Public methods include `setConnectionConfigurator()` and `authenticate()`. Helpers include `wrapExceptionWithMessage()`, `getFallBackAuthenticator()`, `isTokenKerberos()`, `isNegotiate()`, `doSpnegoSequence()`, `sendToken()`, and `readToken()`.

Control flow: if the token is unset, `authenticate()` opens an OPTIONS request. A 200 response with a Kerberos token is accepted; a 401 with `WWW-Authenticate: Negotiate` triggers manual GSSAPI token exchange in `doSpnegoSequence()`; otherwise it instantiates and runs `PseudoAuthenticator`. The SPNEGO sequence obtains or logs into a subject, creates a GSS context for `HTTP/<host>`, loops sending and reading base64 negotiation tokens until established, then the cookie handler captures the server token.

State and persistence: instance state stores current URL, Base64 codec, and configurator for a single authentication flow. Kerberos credentials come from the current subject or ticket cache; no credentials are persisted by this class. Token state is stored in `AuthenticatedURL.Token`.

Dependencies and integration points: depends on GSSAPI, JAAS, Hadoop `KerberosUtil`/`SubjectUtil`, `AuthToken`, commons-codec Base64, HTTP constants, and fallback pseudo auth. Covered by `TestKerberosAuthenticator`.

Risks and test signals: fallback to pseudo auth may be insecure if a service was expected to require Kerberos. `readToken()` assumes `Negotiate ` with a token after the prefix and can fail on bare `Negotiate`. Exception wrapping uses reflection and may fail for exception classes without a string constructor. Test signals include MiniKDC SPNEGO success, fallback behavior, existing token no-op, configurator propagation, and invalid negotiation headers.
