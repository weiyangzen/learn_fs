# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestCertificateUtil.java

Purpose: Tests RSA public-key parsing from PEM-like certificate/base64 data in `CertificateUtil.parseRSAPublicKey`.

Important APIs and control flow: three tests pass a string to `parseRSAPublicKey`: one with PEM header/footer, one with corrupt base64 tail, and one valid base64 certificate body. Invalid inputs expect `ServletException` messages containing `PEM header` or `corrupt`; the valid input asserts a non-null `RSAPublicKey` with algorithm `RSA`.

State and dependencies: all state is literal certificate data embedded in the test. Dependencies are Java security interfaces, servlet exception type, and JUnit.

Integration points: supports JWT redirect authentication public-key provisioning, where configuration likely supplies certificate text. The test clarifies that this utility expects raw base64 body without header/footer.

Risks and test signals: the tests assert error-message substrings, which can be brittle. They do not validate modulus/exponent values, only the key algorithm, so malformed-but-parseable certificate substitutions might pass if they still produce RSA keys.
