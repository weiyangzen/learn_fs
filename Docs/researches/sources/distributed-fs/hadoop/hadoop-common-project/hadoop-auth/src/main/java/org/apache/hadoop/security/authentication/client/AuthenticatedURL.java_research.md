# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/client/AuthenticatedURL.java

Purpose: client-side helper for using `HttpURLConnection` with servers protected by Hadoop `AuthenticationFilter`. It manages the `hadoop.auth` cookie token and delegates initial authentication to an `Authenticator`.

Important APIs, types, and functions: constant `AUTH_COOKIE` is `hadoop.auth`. Nested `AuthCookieHandler` stores and emits the authentication cookie, parses `Set-Cookie`, shortens max-age to 90%, quotes v0 cookie values, and removes expired/empty cookies. Nested `Token` wraps the cookie handler, provides `isSet()`, package-private `set()`, `openConnection()`, and `toString()`. Static default authenticator is `KerberosAuthenticator`. Public APIs include constructors, `setDefaultAuthenticator()`, `getDefaultAuthenticator()`, `openConnection(URL, Token)`, `injectToken()`, and `extractToken()`.

Control flow: `openConnection()` validates HTTP(S) URL and token, calls `authenticator.authenticate(url, token)`, then opens the actual connection through the token's cookie handler. `Token.openConnection()` temporarily installs a global `CookieHandler` under a class lock to let `URL.openConnection()` attach cookies, then restores the previous handler. `extractToken()` treats 200/201/202 as success, 404 as `FileNotFoundException`, and other statuses as authentication failures while clearing the token.

State and persistence: token/cookie state is in memory inside `Token`; no disk persistence. `DEFAULT_AUTHENTICATOR` is static global mutable process state. The temporary global `CookieHandler` swap is synchronized but still a sensitive integration point.

Dependencies and integration points: depends on Hadoop auth server constants, `Authenticator` implementations, `HttpURLConnection`, Java `CookieHandler`/`HttpCookie`, and optional `ConnectionConfigurator` for TLS/timeouts/proxies. Tested by `TestAuthenticatedURL`.

Risks and test signals: instances are documented non-thread-safe. Global default authenticator changes affect all future default instances. Cookie parsing ignores malformed headers and token string printing can reveal credentials. Test signals include cookie extraction/injection, expiry behavior, 404/error handling, configurator invocation, and Kerberos/Pseudo authenticator integration.
