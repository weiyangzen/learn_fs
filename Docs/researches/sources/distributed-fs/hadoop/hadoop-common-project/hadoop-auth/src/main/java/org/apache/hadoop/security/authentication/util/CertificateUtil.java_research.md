<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/CertificateUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/CertificateUtil.java

## Purpose
Parses an RSA public key from a configured PEM certificate body for authentication components that need an X.509 public key.

## Important APIs, types, and functions
`parseRSAPublicKey(String pem)` wraps the supplied body with certificate header/footer, feeds it to an X.509 `CertificateFactory`, extracts `X509Certificate.getPublicKey()`, and casts the result to `RSAPublicKey`.

## Control flow
The method constructs a full PEM string, parses it from a UTF-8 byte stream, and translates `CertificateException` into `ServletException` with a more specific message if the caller included header/footer text.

## State and persistence
The utility is stateless and persists nothing.

## Dependencies and integration points
Depends on Java security certificate APIs, `RSAPublicKey`, UTF-8 encoding, and servlet exceptions. It is typically used by servlet/filter configuration that carries public certificate material.

## Risks and test signals
The unchecked cast can throw `ClassCastException` for non-RSA certificates. `pem.startsWith(PEM_HEADER)` is only reached after a parsing failure and will throw if `pem` is null. Tests should cover valid RSA certs, certs with included header/footer, corrupt PEM, null input, and non-RSA public keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/CertificateUtil.java -->
