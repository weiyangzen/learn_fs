# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationToken.java

Purpose: server-side authenticated principal token used by `AuthenticationFilter` and exposed as the servlet request principal.

Important APIs, types, and functions: extends `AuthToken`, defines singleton `ANONYMOUS`, constructors from user/principal/type and from parsed `AuthToken`, overrides `setMaxInactives()` and `setExpires()` to ignore changes to `ANONYMOUS`, exposes `isExpired()`, and static `parse(String)`.

Control flow: authentication handlers create tokens; the filter sets expiry/inactivity, signs serialized token strings into cookies, parses tokens from cookies, and wraps requests so `getUserPrincipal()` returns the token.

State and persistence: token fields are inherited from `AuthToken` and serialized into signed cookies. `ANONYMOUS` is static and intentionally immutable for expiry updates.

Dependencies and integration points: depends on `AuthToken`, `AuthenticationException`, and servlet principal expectations. Covered by `TestAuthenticationToken`.

Risks and test signals: token trust depends on outer signature verification, not the serialized string alone. Anonymous token must not accidentally become persistent or mutable. Test signals include parse/serialize round trips, expiry/max-inactive behavior, and anonymous immutability.
