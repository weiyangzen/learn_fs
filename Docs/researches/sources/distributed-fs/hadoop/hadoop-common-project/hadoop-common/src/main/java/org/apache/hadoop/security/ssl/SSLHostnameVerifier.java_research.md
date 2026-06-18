# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/SSLHostnameVerifier.java

## Purpose

`SSLHostnameVerifier` defines Hadoop's hostname verification strategies for X.509 certificates and provides built-in verifier instances ranging from strict checks to allow-all.

## Important APIs, Types, and Functions

It extends `javax.net.ssl.HostnameVerifier` and adds `check` overloads for host/socket, host/certificate, CN/subjectAlt arrays, and multi-host checks. Built-ins are `DEFAULT`, `DEFAULT_AND_LOCALHOST`, `STRICT`, `STRICT_IE6`, and `ALLOW_ALL`. Nested `AbstractVerifier` implements most logic, and nested `Certificates` extracts CNs and DNS subjectAlt names.

## Control Flow

`verify` extracts the peer certificate and calls `check`. Socket checks force session/handshake availability when needed. Certificate checks extract CNs and subject alts, then strategy-specific implementations call the shared check with flags for IE6 multi-CN behavior and strict wildcard subdomain matching. Matching normalizes hosts, prefers subject alts plus the first CN, handles wildcards, rejects risky country-code wildcard patterns, and throws `SSLException` on mismatch.

## State and Persistence Behavior

Verifier instances are stateless singletons. Static sorted arrays define disallowed country-code second-level wildcard segments and localhost names.

## Dependencies and Integration Points

It depends on JSSE `SSLSession`, `SSLSocket`, `X509Certificate`, Hadoop `StringUtils`, and SLF4J. `SSLFactory` selects one of these verifiers from configuration.

## Risks and Edge Cases

`ALLOW_ALL` disables hostname verification. CN parsing uses string tokenization of the X500 principal and can be less robust than a full RFC 2253 parser. SubjectAlt extraction only uses DNS type 2, not IP address SANs. `isIP4Address` checks the first character repeatedly inside a loop, which is unusual and should be regression-tested before changes.

## Test Signals

Tests should cover exact CN, DNS SAN precedence, wildcard matching in default and strict modes, localhost relaxation, allow-all behavior, bad country wildcard rejection, IP and SAN edge cases, failed peer verification, and CN extraction with escaped/complex principals.
