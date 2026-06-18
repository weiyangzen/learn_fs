# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestKerberosAuthenticationHandler.java

Purpose: Tests the SPNEGO/Kerberos server-side authentication handler, including initialization, name-rule behavior, dynamic principal discovery, request challenge responses, successful GSS negotiation, invalid token handling, and endpoint whitelist bypass.

Important APIs and control flow: `setup()` creates client and server principals in a MiniKDC keytab, builds default properties for `PRINCIPAL`, `KEYTAB`, `NAME_RULES`, `RULE_MECHANISM`, and `ENDPOINT_WHITELIST`, then initializes `KerberosAuthenticationHandler`. Tests inspect `getKeytab`, `getPrincipals`, `getType`, and call `authenticate(request, response)`. The valid authorization path uses `KerberosTestUtils.doAsClient` to create a GSS context for the server principal, encodes the initial SPNEGO token with Apache Commons Codec `Base64`, and passes it as `Authorization: Negotiate ...`.

State and dependencies: persistent state is the MiniKDC keytab and global `KerberosName` rule configuration. The test depends on JGSS, KerberosTestUtils, Hadoop `KerberosUtil`, servlet mocks, and Kerberos authenticator header constants. `@Timeout(60)` guards external KDC/GSS stalls.

Integration points: exercises dynamic discovery when `PRINCIPAL=*`, accepting only `HTTP/` principals and rejecting keytabs without matching principals. It validates challenge headers for missing/invalid authorization, incomplete header errors, response OK/UNAUTHORIZED decisions after GSS token processing, and whitelist behavior for paths such as `/white`.

Risks and test signals: global Kerberos name rules can leak between tests if handler initialization changes; teardown destroys the handler but does not independently reset every static rule. The valid GSS path may legitimately return null during multi-step negotiation and asserts both OK-token and challenge-continuation outcomes. Header construction in invalid Kerberos tests omits a space after `Negotiate`, which specifically guards parser strictness.
