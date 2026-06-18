# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/JWTRedirectAuthenticationHandler.java

Purpose: browser-oriented alternate Kerberos handler that redirects unauthenticated UI users to a WebSSO provider, validates an RS256 JWT returned in a cookie, and issues a Hadoop `AuthenticationToken`.

Important APIs, types, and functions: config properties are `authentication.provider.url`, `public.key.pem`, `expected.jwt.audiences`, and `jwt.cookie.name`. State includes auth provider URL, RSA public key, accepted audiences, and cookie name. Public/test APIs include `setPublicKey()`, `init()`, `alternateAuthenticate()`, `getJWTFromCookie()`, and `constructLoginURL()`. Validation helpers are `validateToken()`, `validateSignature()`, `validateAudiences()`, and `validateExpiration()`.

Control flow: initialization requires an auth provider URL and RSA public key, parses optional audience and cookie settings, and delegates base Kerberos setup to `AltKerberosAuthenticationHandler`. Browser requests without a JWT cookie are redirected to the provider with `originalUrl=<current URL plus query>`. Requests with a JWT parse it, validate signature/audience/expiration, extract subject as username, and return an `AuthenticationToken`; invalid tokens trigger a new redirect.

State and persistence: handler stores validation configuration in memory. JWTs persist client-side in the configured cookie. Hadoop auth tokens are then signed and persisted by `AuthenticationFilter` in the normal `hadoop.auth` cookie.

Dependencies and integration points: extends `AltKerberosAuthenticationHandler`; depends on Nimbus JOSE JWT, RSA public keys from `CertificateUtil`, servlet redirects/cookies, and Hadoop auth tokens. Covered by `TestJWTRedirectAuthenticationHandler`.

Risks and test signals: `constructLoginURL()` concatenates the original URL and query without URL encoding, which can break redirects or allow parameter confusion. If expected audiences are unset, any audience is accepted. Expiration treats missing expiration as valid. Logs include usernames and serialized invalid JWTs. Test signals include redirect construction, cookie extraction, signature failure/success, audience matching, expiration handling, custom cookie names, and non-browser Kerberos fallback.
