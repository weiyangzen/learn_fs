# Research: subset-b-007136

This grouped report covers the requested Hadoop authentication test utilities, authentication handler tests, native-build CMake helpers, and FindBugs exclusion configuration. Each file section is bounded by reconciliation markers for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestJWTRedirectAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestJWTRedirectAuthenticationHandler.java

Purpose: JUnit 5 tests for `JWTRedirectAuthenticationHandler`, a Kerberos-derived alternate authentication handler that accepts a signed JWT cookie or redirects clients to an external authentication provider. The class extends `KerberosSecurityTestcase`, creates MiniKDC principals for HTTP services, and generates RSA key pairs plus Nimbus `SignedJWT` instances for validation scenarios.

Important APIs and control flow: tests call `handler.setPublicKey`, `handler.init(Properties)`, `alternateAuthenticate(request, response)`, and `constructLoginURL(request)`. `getProperties()` supplies `AUTHENTICATION_PROVIDER_URL`, `kerberos.principal`, and `kerberos.keytab`; individual tests mutate properties for custom cookie name, missing provider URL, and audience validation. `getJWT` builds claims with subject, issue time, issuer, scope, audience `bar`, and optional expiration, signs with `RSASSASigner`, then stores the serialized JWT in a servlet `Cookie`.

State and dependencies: per-test state includes RSA keys, the handler instance, Kerberos keytab contents, mocked servlet request/response objects, and JWT claims. The file depends on Nimbus JOSE/JWT, Mockito, servlet APIs, MiniKDC, and Hadoop Kerberos test utilities. Persistent external state is limited to the generated keytab managed by the test base.

Integration points: verifies signature validation, expiration handling, audience checking, JWT cookie naming, provider URL configuration, redirect URL encoding, and original URL query-string propagation. Successful JWTs produce `AuthenticationToken` usernames from `sub`; invalid parse/signature/expiration/audience cases trigger `sendRedirect` to the provider URL with `originalUrl`.

Risks and test signals: negative tests expect specific exception messages for missing public key and provider URL, which can be brittle if production diagnostics change. Date-based expiration uses short offsets but does not sleep, so it is relatively stable. Redirect expectation depends on exact URL concatenation and query string handling, making it a good regression signal for login URL construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestJWTRedirectAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestKerberosAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestKerberosAuthenticationHandler.java

Purpose: Tests the SPNEGO/Kerberos server-side authentication handler, including initialization, name-rule behavior, dynamic principal discovery, request challenge responses, successful GSS negotiation, invalid token handling, and endpoint whitelist bypass.

Important APIs and control flow: `setup()` creates client and server principals in a MiniKDC keytab, builds default properties for `PRINCIPAL`, `KEYTAB`, `NAME_RULES`, `RULE_MECHANISM`, and `ENDPOINT_WHITELIST`, then initializes `KerberosAuthenticationHandler`. Tests inspect `getKeytab`, `getPrincipals`, `getType`, and call `authenticate(request, response)`. The valid authorization path uses `KerberosTestUtils.doAsClient` to create a GSS context for the server principal, encodes the initial SPNEGO token with Apache Commons Codec `Base64`, and passes it as `Authorization: Negotiate ...`.

State and dependencies: persistent state is the MiniKDC keytab and global `KerberosName` rule configuration. The test depends on JGSS, KerberosTestUtils, Hadoop `KerberosUtil`, servlet mocks, and Kerberos authenticator header constants. `@Timeout(60)` guards external KDC/GSS stalls.

Integration points: exercises dynamic discovery when `PRINCIPAL=*`, accepting only `HTTP/` principals and rejecting keytabs without matching principals. It validates challenge headers for missing/invalid authorization, incomplete header errors, response OK/UNAUTHORIZED decisions after GSS token processing, and whitelist behavior for paths such as `/white`.

Risks and test signals: global Kerberos name rules can leak between tests if handler initialization changes; teardown destroys the handler but does not independently reset every static rule. The valid GSS path may legitimately return null during multi-step negotiation and asserts both OK-token and challenge-continuation outcomes. Header construction in invalid Kerberos tests omits a space after `Negotiate`, which specifically guards parser strictness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestKerberosAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestLdapAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestLdapAuthenticationHandler.java

Purpose: Integration-style unit tests for `LdapAuthenticationHandler`, verifying HTTP Basic authentication against an embedded Apache Directory LDAP server populated with one user entry.

Important APIs and control flow: class-level ApacheDS annotations create an LDAP server, partition, base DN, and LDIF entry `uid=bjones` with password `p@ssw0rd`. `setup()` initializes `LdapAuthenticationHandler` using `BASE_DN` and `PROVIDER_URL`. Tests call `authenticate(request, response)` with missing, malformed, valid, invalid, and wrong credentials. Credentials are base64-encoded and prefixed with `Basic` only on complete cases.

State and dependencies: runtime state is the in-process LDAP directory, handler instance, and mocked servlet request/response. Dependencies include Apache Directory test extensions, Commons Codec `Base64`, servlet APIs, Hadoop LDAP constants, and `AuthenticationException`.

Integration points: confirms unauthenticated requests receive `WWW-Authenticate: Basic` and `401`, valid LDAP bind yields an `AuthenticationToken` of handler `TYPE` with username/name `bjones` and HTTP 200, incomplete auth returns null, and wrong password raises `AuthenticationException`.

Risks and test signals: because it spins up ApacheDS, failures can reflect embedded server startup or port binding rather than handler logic. Timeouts limit hangs. The invalid-authorization test supplies base64 credentials without the `Basic` scheme, intentionally asserting that malformed headers are challenged rather than bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestLdapAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestMultiSchemeAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestMultiSchemeAuthenticationHandler.java

Purpose: Tests `MultiSchemeAuthenticationHandler`, which advertises and dispatches multiple HTTP authentication schemes, configured here as `Basic` backed by LDAP and `Negotiate` backed by Kerberos.

Important APIs and control flow: the test creates an embedded LDAP server through ApacheDS annotations and manually starts a `KerberosSecurityTestcase` MiniKDC in `setUp()`. `getDefaultProperties()` sets `SCHEMES_PROPERTY`, per-scheme `AUTH_HANDLER_PROPERTY` values, Kerberos principal/keytab/name rules, and LDAP base/provider URL. Tests call `handler.authenticate` for missing authorization, malformed authorization, valid LDAP Basic credentials, and invalid Kerberos Negotiate data.

State and dependencies: state spans two external test services: ApacheDS and MiniKDC, plus a generated keytab and handler sub-handlers. Dependencies include Hadoop Kerberos and LDAP handlers, servlet mocks, `HttpConstants`, Apache Directory, and Commons Codec.

Integration points: verifies that missing or unusable authorization adds both `WWW-Authenticate` challenges (`Basic` and `Negotiate`) and returns 401. The valid Basic path confirms dispatch to LDAP and token type `ldap`; the invalid Negotiate path confirms dispatch to Kerberos and propagation of `AuthenticationException`.

Risks and test signals: the test does not exercise a fully valid Kerberos SPNEGO success through the multi-scheme wrapper, only invalid Kerberos dispatch and valid LDAP dispatch. It also starts/stops MiniKDC separately from the ApacheDS extension, so teardown ordering is significant. Exact scheme strings and property keys are strong compatibility signals for production configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestMultiSchemeAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestPseudoAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestPseudoAuthenticationHandler.java

Purpose: Unit tests for simple pseudo authentication, where a username can be supplied through the pseudo-auth query parameter and anonymous access may be enabled or disabled.

Important APIs and control flow: tests instantiate `PseudoAuthenticationHandler`, initialize it with `ANONYMOUS_ALLOWED`, inspect `getAcceptAnonymous` and `getType`, and call `authenticate(request, response)`. `_testUserName` parameterizes the username path for anonymous enabled and disabled modes by mocking `request.getQueryString()` as `user.name=user` via `PseudoAuthenticator.USER_NAME`.

State and dependencies: state is confined to the handler instance and mocked servlet request/response. Dependencies are JUnit, Mockito, servlet APIs, `PseudoAuthenticator`, and `AuthenticationToken`.

Integration points: verifies anonymous mode returns `AuthenticationToken.ANONYMOUS`, non-anonymous mode without a username returns null, and a query-string username always produces a token with name/user `user` and handler type `simple`.

Risks and test signals: tests do not assert response headers/status for missing credentials, focusing only on token return values. The query parsing assertion is a direct signal for compatibility between client-side `PseudoAuthenticator.USER_NAME` and server handler parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestPseudoAuthenticationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/StringSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/StringSignerSecretProvider.java

Purpose: Test-only `SignerSecretProvider` implementation that derives a single signing secret from the `AuthenticationFilter.SIGNATURE_SECRET` string property.

Important APIs and control flow: `init(Properties, ServletContext, long)` reads `signatureSecret`, converts it to UTF-8 bytes, stores it in `secret`, and exposes it as a one-element `byte[][] secrets`. `getCurrentSecret()` returns the current byte array; `getAllSecrets()` returns the one-element array. There is no rollover, destruction, validation, or servlet-context behavior.

State and dependencies: state is two fields, `secret` and `secrets`, both initialized once. It depends on Hadoop classification annotations, `AuthenticationFilter`, servlet context type, and `StandardCharsets.UTF_8`.

Integration points: used by signer tests and created through `StringSignerSecretProviderCreator` because the class is package-private. It models the simplest static-secret provider contract used by `Signer`.

Risks and test signals: missing `SIGNATURE_SECRET` would throw a null dereference during `getBytes`, so callers must configure it. The provider returns internal byte arrays directly, matching test utility simplicity but not defensive-copy behavior. Its stability annotations mark it visible/testing and unstable, so production code should not depend on it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/StringSignerSecretProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/StringSignerSecretProviderCreator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/StringSignerSecretProviderCreator.java

Purpose: Public test helper that exposes construction of the package-private `StringSignerSecretProvider` for unit tests or other test packages.

Important APIs and control flow: the only API is static `newStringSignerSecretProvider()`, declared to throw `Exception`, which returns `new StringSignerSecretProvider()`. It performs no initialization; callers must still call `init` with the signature secret property.

State and dependencies: the class has no fields or persistence. It depends only on Hadoop `VisibleForTesting` and `InterfaceStability.Unstable` annotations plus the package-private provider type.

Integration points: bridges Java access control for tests that need a concrete `SignerSecretProvider` with deterministic string-backed secrets. It keeps test code from making `StringSignerSecretProvider` itself public.

Risks and test signals: the wide `throws Exception` is unnecessary for current construction but preserves flexibility. The helper can expose unstable test-only API outside the package, so usage should remain in test scope.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/StringSignerSecretProviderCreator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestAuthToken.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestAuthToken.java

Purpose: Unit tests for `AuthToken`, covering constructor validation, getters, expiration behavior, string serialization, and parser tolerance for quoted or signed-token suffix forms.

Important APIs and control flow: tests instantiate `AuthToken(user, principal, type)`, call `setExpires`, `getUserName`, `getName`, `getType`, `getExpires`, `isExpired`, `toString`, and static `parse`. Constructor tests expect `IllegalArgumentException` for null or empty username, principal, and type. Parser tests accept quoted serialized tokens and strings with an extra `&s=1234` signature parameter, then reject strings missing the expiration field.

State and dependencies: token state is in-memory user/name/type/expiry fields. Tests use `System.currentTimeMillis() + 50` and `Thread.sleep(70)` to verify expiration. Dependency surface is JUnit and Hadoop `AuthenticationException`.

Integration points: validates the token wire format consumed by authentication cookie/signing code. The parser’s tolerance of appended signature data is important for signed cookie extraction.

Risks and test signals: the sleep-based expiration checks are timing-sensitive, with only 20 ms fuzz beyond the 50 ms expiry. Slow or overloaded CI could make these flaky. Negative parser coverage is narrow but protects required-field enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestAuthToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestCertificateUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestCertificateUtil.java

Purpose: Tests RSA public-key parsing from PEM-like certificate/base64 data in `CertificateUtil.parseRSAPublicKey`.

Important APIs and control flow: three tests pass a string to `parseRSAPublicKey`: one with PEM header/footer, one with corrupt base64 tail, and one valid base64 certificate body. Invalid inputs expect `ServletException` messages containing `PEM header` or `corrupt`; the valid input asserts a non-null `RSAPublicKey` with algorithm `RSA`.

State and dependencies: all state is literal certificate data embedded in the test. Dependencies are Java security interfaces, servlet exception type, and JUnit.

Integration points: supports JWT redirect authentication public-key provisioning, where configuration likely supplies certificate text. The test clarifies that this utility expects raw base64 body without header/footer.

Risks and test signals: the tests assert error-message substrings, which can be brittle. They do not validate modulus/exponent values, only the key algorithm, so malformed-but-parseable certificate substitutions might pass if they still produce RSA keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestCertificateUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestFileSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestFileSignerSecretProvider.java

Purpose: Unit tests for `FileSignerSecretProvider`, ensuring secrets can be loaded from a configured file and that empty secret files fail fast.

Important APIs and control flow: `testGetSecrets` creates `target/test-dir/http-secret.txt` under `test.build.data` fallback, writes `hadoop`, initializes the provider with `AuthenticationFilter.SIGNATURE_SECRET_FILE`, then checks `getCurrentSecret()` and `getAllSecrets()`. `testEmptySecretFileThrows` creates an empty temp file and expects `RuntimeException` during `init`, with a message starting `No secret in signature secret file:`.

State and dependencies: state is filesystem-backed secret content and provider byte arrays. Dependencies include Java `FileWriter`, JUnit assertions, and `AuthenticationFilter` configuration keys.

Integration points: covers static secret file loading for authentication cookie signing. The one-element all-secrets result confirms no rollover or previous-secret support in this provider.

Risks and test signals: the first test does not clean up the generated file, relying on build temp-directory lifecycle. It uses platform default charset for expected bytes and file writing, unlike the string provider’s UTF-8, which can matter on unusual default encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestFileSignerSecretProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestJaasConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestJaasConfiguration.java

Purpose: Tests `JaasConfiguration` construction of Kerberos login-module entries without performing actual Kerberos authentication.

Important APIs and control flow: the test selects the expected login module name from `java.vendor` (`com.ibm...Krb5LoginModule` for IBM, otherwise `com.sun...Krb5LoginModule`). It constructs `JaasConfiguration("foo", "foo/localhost", "/some/location/foo.keytab")`, verifies unknown entry name `bar` returns null, then inspects entry `foo` for `REQUIRED` control flag and six exact options: `keyTab`, `principal`, `useKeyTab`, `storeKey`, `useTicketCache`, and `refreshKrb5Config`.

State and dependencies: no external Kerberos state is used. Dependencies are JAAS `AppConfigurationEntry`, system property `java.vendor`, JUnit, and Java collections.

Integration points: validates the JAAS configuration used by Kerberos-enabled ZooKeeper clients and authentication utilities.

Risks and test signals: hard-coded option count catches accidental additions/removals but may be too strict for platform-specific JAAS needs. The vendor branch ensures IBM Java remains supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestJaasConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestKerberosName.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestKerberosName.java

Purpose: Tests `KerberosName` principal parsing and rule-based short-name translation for Hadoop and MIT rule mechanisms.

Important APIs and control flow: `setUp()` sets Kerberos realm/KDC system properties and installs a multi-rule Hadoop rule set. `checkTranslation`, `checkBadName`, and `checkBadTranslation` wrap creation and `getShortName()` assertions. Tests cover one-part, two-part, admin/root special rules, anti-pattern principal syntax, Hadoop-vs-MIT unmatched translation behavior, service/host/realm parsing accessors, lower-case `/L` rule suffixes, and invalid mechanism rejection.

State and dependencies: global state includes Java security krb5 system properties and static `KerberosName` rules/mechanism. `@AfterEach` clears the system properties but does not reset rules. Dependencies include `KerberosTestUtils`, IOException behavior, and JUnit.

Integration points: name translation is used by Kerberos authentication handlers to map Kerberos principals to local user names. The tests encode important compatibility between Hadoop-style rules, MIT-style fallback, regex replacements, and lower-casing.

Risks and test signals: global static rule state can interact with other tests if execution order or parallelism changes. The tests intentionally print rules/translations to stdout, useful for diagnostics but noisy. Parsing checks demonstrate accepted forms: service/host@realm, service/host without realm, and service@realm without host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestKerberosName.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestKerberosUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestKerberosUtil.java

Purpose: Tests miscellaneous Kerberos utility behavior: service-principal construction, keytab principal extraction and filtering, and ASN.1 token server-principal decoding.

Important APIs and control flow: `testGetServerPrincipal` checks `KerberosUtil.getServicePrincipal` for null, empty, wildcard `0.0.0.0`, uppercase, and lowercase hosts, using `getLocalHostName`, `getDefaultRealmProtected`, and `getDomainRealm` assumptions. Keytab tests create a synthetic keytab with Apache Kerby `Keytab`, adding three kvnos per principal to ensure `getPrincipalNames` deduplicates entries and regex filtering works. `testServicePrincipalDecode` decodes embedded base64 krb5 and SPNEGO tokens and verifies `getTokenServerName`.

State and dependencies: persistent state is a local `test.keytab`, deleted in `@AfterEach`. Dependencies include Apache Kerby keytab types, Java regex, base64, locale, and Hadoop `KerberosUtil`.

Integration points: principal construction affects service login names and host canonicalization; keytab discovery is used by dynamic Kerberos handler principal loading; token decoding supports audit/routing of SPNEGO/Kerberos tokens.

Risks and test signals: `testGetServerPrincipal` depends on local realm/domain lookup behavior and may be environment-sensitive. `deleteKeytab` ignores deletion failure. The embedded binary-token strings provide strong regression coverage for ASN.1 parsing but are opaque and hard to update safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestKerberosUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestRandomSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestRandomSignerSecretProvider.java

Purpose: Tests `RandomSignerSecretProvider` rollover scheduling and secret-array semantics using deterministic random seeds.

Important APIs and control flow: a spy subclass overrides `rollSecret()` as a no-op so Mockito can verify the scheduler calls it, while `realRollSecret()` delegates to `super.rollSecret()` for controlled state transitions. The test predicts three 32-byte secrets from a seeded `Random`, initializes the provider with a 250 ms rollover frequency, verifies initial current/previous slots, waits for scheduled roll invocations with Mockito `timeout`, then manually rolls and validates current and previous secret positions.

State and dependencies: state includes scheduled background rollover, current/previous secret arrays, and deterministic RNG seed. Dependencies include Mockito spy/timeout, Log4j level configuration, and JUnit.

Integration points: protects the `SignerSecretProvider` contract expected by `Signer`: current secret at index 0 and previous at index 1 during rollover windows.

Risks and test signals: scheduler timing is inherently flaky under heavy load, though the no-op override avoids races in state mutation. Seed from `System.currentTimeMillis()` is deterministic only within each run because expected secrets are generated from the same seed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestRandomSignerSecretProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestRolloverSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestRolloverSignerSecretProvider.java

Purpose: Tests the abstract `RolloverSignerSecretProvider` base behavior using a deterministic subclass that returns a fixed sequence of byte-array secrets.

Important APIs and control flow: inner `TRolloverSignerSecretProvider` overrides `generateNewSecret()` to return `doctor`, `who`, then `tardis`. The test initializes with a 15-second rollover frequency, checks initial current secret and null previous slot, sleeps beyond each rollover interval, and verifies the two-secret window after each scheduled rollover.

State and dependencies: state is the provider’s scheduler plus current/previous secret array. Dependencies are JUnit and the base provider class. `destroy()` is called in a finally block to stop background scheduling.

Integration points: establishes the shared rollover contract inherited by random and ZooKeeper signer providers: current secret at `allSecrets[0]`, previous accepted secret at `allSecrets[1]`.

Risks and test signals: this is a slow timing test with sleeps of roughly 17 seconds per rollover, making it expensive and potentially flaky. It directly tests scheduler behavior rather than using controlled manual rolls, so runtime delays can affect it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestRolloverSignerSecretProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestSigner.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestSigner.java

Purpose: Tests HMAC-style string signing and verification through `Signer`, including invalid input, deterministic signatures, tamper detection, and multiple-secret rollover compatibility.

Important APIs and control flow: tests construct `Signer` with a string-backed provider, call `sign(text)`, and call `verifyAndExtract(signedText)`. Null and empty input must throw `IllegalArgumentException`; unsigned or tampered text must throw `SignerException`; repeated signing with the same secret and text must be stable. `testMultipleSecrets` uses an inner mutable `SignerSecretProvider` exposing current and previous secrets to validate that signing uses only the current secret and verification accepts both current and previous until the old secret falls out.

State and dependencies: state is provider-managed byte-array secrets and signed string text. Dependencies include servlet context type for the provider contract, `AuthenticationFilter.SIGNATURE_SECRET`, and JUnit.

Integration points: this file is the main behavioral contract for authentication cookie signing and rolling secret acceptance. It confirms backwards verification during one rollover window and rejection after two rotations.

Risks and test signals: the inner provider uses platform default charset for string bytes, while production providers may use explicit charsets. Equality of signatures across `secretB` current and `secretA` previous confirms current-only signing, but the comment on `assertNotEquals(s1, s3)` is misleading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestSigner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestStringSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestStringSignerSecretProvider.java

Purpose: Minimal unit test for `StringSignerSecretProvider`, checking that a configured string secret is exposed as the current and only signing secret.

Important APIs and control flow: the test creates a provider, sets `AuthenticationFilter.SIGNATURE_SECRET` to `secret`, calls `init`, and asserts `getCurrentSecret()` and `getAllSecrets()[0]` match `secret.getBytes()`, with exactly one available secret.

State and dependencies: state is a one-element byte-array secret. Dependencies are JUnit and `AuthenticationFilter`.

Integration points: supports `Signer` tests and validates the test-only static provider contract.

Risks and test signals: expected bytes use platform default charset while the provider itself uses UTF-8; ASCII `secret` avoids differences. It does not test null/missing secret behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestStringSignerSecretProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestSubjectUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestSubjectUtil.java

Purpose: Tests `SubjectUtil`, a compatibility layer over Java `Subject` execution APIs across Java versions, focusing on exception propagation semantics for `doAs`, `callAs`, `current`, and `sneakyThrow`.

Important APIs and control flow: the test computes `JAVA_SPEC_VER`, asserts `SubjectUtil.HAS_CALL_AS` for Java versions above 17, and exercises `doAs(Subject, PrivilegedAction)`, `doAs(Subject, PrivilegedExceptionAction)`, `callAs(Subject, Callable)`, and `sneakyThrow`. It checks checked exceptions, `PrivilegedActionException`, runtime exceptions, `CompletionException`, `LinkageError`, and null action handling. Assertions branch for Java versions above 11 where `PrivilegedAction` checked-exception propagation differs.

State and dependencies: state is mostly Java runtime version behavior and the current subject. Dependencies are JAAS/security privileged action APIs, `Callable`, `CompletionException`, JUnit 5 assert helpers, and `IOException`.

Integration points: Hadoop authentication code uses subject-scoped execution for Kerberos and secure client actions. These tests preserve compatibility across Java LTS transitions and newer `Subject.callAs` behavior.

Risks and test signals: assertions depend tightly on Java exception wrapping and message text, which can change between JDK implementations. The version parser handles `1.8`, `9`, and later numeric forms but assumes a simple first component. The tests are strong signals for not accidentally double-wrapping or swallowing exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestSubjectUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestZKSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestZKSignerSecretProvider.java

Purpose: Integration tests for `ZKSignerSecretProvider`, validating ZooKeeper-backed shared signing-secret initialization, rollover, upgrade from older secret lengths, and coordination between multiple provider instances.

Important APIs and control flow: `@BeforeEach` starts a Curator `TestingServer`; tests configure `ZOOKEEPER_CONNECTION_STRING` and `ZOOKEEPER_PATH`. Like the random provider test, `MockZKSignerSecretProvider` overrides scheduled `rollSecret()` for Mockito verification and exposes `realRollSecret()`. `testOne` verifies single-provider current/previous secrets. `testUpgradeChangeSecretLength` seeds ZooKeeper with an old provider that generates stringified `long` secrets, then initializes the new provider and verifies preserved old secrets plus later 32-byte generated secrets. `testMultiple` initializes two providers with different seeds and tests race winners for coordinated rolls.

State and dependencies: persistent test state is the ZooKeeper znode data under `/secret`; runtime state includes background schedulers and provider local caches. Dependencies include Curator `TestingServer`, servlet context mocks, Mockito, Log4j, and Java `Random`.

Integration points: covers distributed secret sharing for authentication filters across multiple servers. It validates that all providers converge to the same secret window and that old secret-length data remains readable through upgrade.

Risks and test signals: tests are timing-sensitive through scheduler verification and rely on deterministic interleaving via manual `realRollSecret()` calls. Multi-provider scenarios intentionally model write races and should catch optimistic-lock/versioning regressions in znode updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestZKSignerSecretProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestZookeeperClientCreation.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestZookeeperClientCreation.java

Purpose: Tests `ZookeeperClient` builder/configurer behavior by spying on Curator `CuratorFrameworkFactory.Builder` and verifying default and customized values for connection, namespace, timeouts, retry policy, ACLs, SASL, and SSL.

Important APIs and control flow: `setup()` creates a spy `ZookeeperClient.configure()`, sets connection string `dummy`, and stubs `createFrameworkFactoryBuilder()`. Positive tests call fluent methods such as `withConnectionString`, `withZookeeperFactory`, `withNamespace`, `withSessionTimeout`, `withConnectionTimeout`, `withRetryPolicy`, `withAuthType("sasl")`, `enableSSL`, `withKeystore`, and `withTruststore`, then verify builder calls. Negative tests assert null/invalid auth, missing SASL keytab/principal/login-entry, and incomplete SSL configuration. Helper methods verify defaults: namespace null, `ConfigurableZookeeperFactory`, 60000 ms session timeout, 15000 ms connection timeout, `ExponentialBackoffRetry(1000,3)`, `DefaultACLProvider`, and default `ZKClientConfig`.

State and dependencies: tests mutate system properties for Curator timeout defaults, Java vendor, ZooKeeper login context, and JAAS `Configuration`; SASL helper restores JAAS and vendor. Dependencies include Curator, ZooKeeper client SSL config, AssertJ, Mockito, and JAAS.

Integration points: this is the configuration contract for ZooKeeper-backed signer providers and other Hadoop-auth ZooKeeper clients. SASL tests assert owner-only ACLs using principal primary name and JAAS login module selection for IBM vs non-IBM Java. SSL tests assert Netty secure client settings and keystore/truststore properties.

Risks and test signals: some tests set system properties and clear them manually; exceptions before cleanup could leak properties. The builder-spy pattern verifies configuration calls rather than opening a real client. Error-message equality is intentionally strict and can break on wording changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestZookeeperClientCreation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/HadoopCommon.cmake -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/HadoopCommon.cmake

Purpose: Shared CMake utility and platform configuration module for Hadoop native components. It centralizes compiler/linker flags, dual static/shared library helpers, output directories, library suffix search behavior, and OS/architecture-specific native build handling.

Important APIs and control flow: macros `hadoop_add_compiler_flags` and `hadoop_add_linker_flags` append flags to global C/C++ and executable/shared linker variables. Functions `hadoop_add_dual_library`, `hadoop_target_link_dual_libraries`, `hadoop_output_directory`, and `hadoop_dual_output_directory` create and configure paired shared/static targets. Library suffix macros adjust `CMAKE_FIND_LIBRARY_SUFFIXES` for versioned or unversioned shared library discovery across Darwin, FreeBSD, Windows, and Unix.

State and dependencies: state is CMake cache/global variables: compiler flags, linker flags, target properties, `CMAKE_SYSTEM_PROCESSOR`, `CMAKE_LIBRARY_ARCHITECTURE`, and C standard. Dependencies include CMake thread detection, `readelf`, `JAVA_JVM_LIBRARY`, `CheckSymbolExists`, and platform identifiers.

Integration points: included by native subprojects before JNI/native library builds. Linux logic adds `_GNU_SOURCE`, suppresses GCC 14 implicit-function-declaration-as-error, handles 32-bit JVM builds with `-m32`, and detects ARM soft-float JVM ABI. Solaris logic requires 64-bit JVM, gcc, POSIX/extension flags, C++98, and processor remapping to amd64/sparcv9.

Risks and test signals: global mutation of flags and processor variables affects all later CMake discovery, especially `FindJNI`. ARM soft-float detection depends on `readelf` and `JAVA_JVM_LIBRARY` being available. The GCC 14 warning suppression may hide real implicit declaration problems while preserving legacy build compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/HadoopCommon.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/HadoopJNI.cmake -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/HadoopJNI.cmake

Purpose: Shared JNI discovery module for Hadoop native components, ensuring the CMake build uses a JVM matching Maven-provided architecture.

Important APIs and control flow: the file first validates `JVM_ARCH_DATA_MODEL` is defined and either 32 or 64. On Linux, it derives `_java_home` from `JAVA_HOME`, maps `CMAKE_SYSTEM_PROCESSOR` to Java library architecture directories (`i386`, `amd64`, `arm`, `ppc64le`/`ppc64`, or processor name), searches only under `JAVA_HOME` for `jni.h`, `jni_md.h` or IBM `jniport.h`, and `jvm`/`JavaVM`. It sets `JNI_INCLUDE_DIRS` and `JNI_LIBRARIES`, emits diagnostic messages, fails if any component is missing, then still invokes `find_package(JNI REQUIRED)`. Non-Linux uses standard `find_package(Java REQUIRED)`, `include(UseJava)`, and `find_package(JNI REQUIRED)`.

State and dependencies: state is CMake variables for Java include paths, JVM library, JNI include/library variables, and temporary `_java_home`/`_java_libarch`. It depends on `JAVA_HOME`, Maven-provided `JVM_ARCH_DATA_MODEL`, CMake `FindJNI`, and Java/JNI installation layout.

Integration points: included by native targets requiring JNI headers or JVM libraries. It cooperates with `HadoopCommon.cmake`, which may alter `CMAKE_SYSTEM_PROCESSOR` for 32-bit builds before JNI discovery.

Risks and test signals: Linux discovery intentionally ignores system paths, so an unset or wrong `JAVA_HOME` is fatal even if system JNI exists. Mixed JDK layouts across Java 8 and later are handled by broad path globs, but unusual vendors can still fail. Diagnostic messages are useful build signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/HadoopJNI.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/findbugsExcludeFile.xml -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/findbugsExcludeFile.xml

Purpose: FindBugs filter file suppressing known or accepted static-analysis findings across Hadoop common, IPC, security, MapReduce compatibility classes, generated protobuf/JSP code, native-backed fields, metrics, crypto enums, and utility classes.

Important APIs and control flow: the XML root `FindBugsFilter` contains many `Match` elements scoped by package, class, field, method, bug pattern, or bug code. Broad suppressions include generated proto packages, exposed representation patterns (`EI_EXPOSE_REP`, `EI_EXPOSE_REP2`), serializable comparator warnings, mutable static warnings under `org.apache.hadoop.*`, XSS/HRS findings for legacy web classes, and generated protobuf regex class names. Narrow suppressions document intentional behavior, such as IPC connection synchronization, SASL cleanup exception handling, `System.exit` usage in task/job driver paths, switch fallthroughs, object cast compatibility, enum setters used by PB helpers, and streams FindBugs believes are unclosed.

State and dependencies: the file is declarative build/test configuration consumed by FindBugs/SpotBugs-style analysis. It does not execute code but changes which warnings fail or appear in analysis results.

Integration points: referenced by Hadoop common build tooling to keep static-analysis output manageable. Comments are part of the maintenance contract, explaining why individual suppressions are accepted or temporary.

Risks and test signals: broad suppressions can hide real defects, especially package-wide `MS`, representation exposure, and generated-code regexes if they match more than intended. There is a likely typo `<Filed name="done"/>` in the `ExternalCall` suppression, which may make that specific filter ineffective. Static-analysis upgrades can rename bug patterns or make old suppressions stale.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/findbugsExcludeFile.xml -->
