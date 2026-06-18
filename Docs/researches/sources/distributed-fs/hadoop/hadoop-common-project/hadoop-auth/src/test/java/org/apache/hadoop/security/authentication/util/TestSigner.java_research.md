# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/util/TestSigner.java

Purpose: Tests HMAC-style string signing and verification through `Signer`, including invalid input, deterministic signatures, tamper detection, and multiple-secret rollover compatibility.

Important APIs and control flow: tests construct `Signer` with a string-backed provider, call `sign(text)`, and call `verifyAndExtract(signedText)`. Null and empty input must throw `IllegalArgumentException`; unsigned or tampered text must throw `SignerException`; repeated signing with the same secret and text must be stable. `testMultipleSecrets` uses an inner mutable `SignerSecretProvider` exposing current and previous secrets to validate that signing uses only the current secret and verification accepts both current and previous until the old secret falls out.

State and dependencies: state is provider-managed byte-array secrets and signed string text. Dependencies include servlet context type for the provider contract, `AuthenticationFilter.SIGNATURE_SECRET`, and JUnit.

Integration points: this file is the main behavioral contract for authentication cookie signing and rolling secret acceptance. It confirms backwards verification during one rollover window and rejection after two rotations.

Risks and test signals: the inner provider uses platform default charset for string bytes, while production providers may use explicit charsets. Equality of signatures across `secretB` current and `secretA` previous confirms current-only signing, but the comment on `assertNotEquals(s1, s3)` is misleading.
