# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AuthenticationHandlerUtil.java

Purpose: static helper for resolving authentication handler names and validating/matching HTTP authentication schemes.

Important APIs, types, and functions: `getAuthenticationHandlerClassName()` maps short names for pseudo, kerberos, LDAP, and multi-scheme handlers to class names, otherwise returns the input. `checkAuthScheme()` canonicalizes Basic, Negotiate, and Digest or throws. `matchAuthScheme()` case-insensitively checks whether an auth header begins with a scheme.

Control flow: `AuthenticationFilter` uses class-name resolution during init. Multi-scheme or handler code can use scheme validation and matching for Authorization headers.

State and persistence: no state; constructor is private.

Dependencies and integration points: depends on `HttpConstants` and handler type constants. Supports pluggability by letting fully qualified class names pass through.

Risks and test signals: `matchAuthScheme()` only checks prefix length, so a header like `BasicXYZ` can match `Basic` even without a delimiter. Null inputs throw `NullPointerException`. Test signals include short-name resolution, custom class pass-through, valid/invalid schemes, and delimiter-sensitive auth matching.
