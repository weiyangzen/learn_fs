<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/Signer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/Signer.java

## Purpose
Signs and verifies string values, primarily Hadoop Auth token cookies, using HMAC-SHA256 and secrets supplied by a `SignerSecretProvider`.

## Important APIs, types, and functions
`sign(String str)` rejects null/empty values, signs with the current secret, and appends `&s=<base64-hmac>`. `verifyAndExtract(String signedStr)` finds the final signature delimiter, verifies against all currently valid secrets, and returns the unsigned value. `computeSignature()` performs HmacSHA256 over UTF-8 bytes and Base64 encodes the MAC. `checkSignatures()` uses `MessageDigest.isEqual()` for comparison.

## Control flow
Signing uses only `getCurrentSecret()`. Verification accepts any non-null secret returned by `getAllSecrets()`, allowing current and previous rollover secrets. Invalid or missing signatures throw `SignerException`.

## State and persistence
The signer stores only the provider reference. Signed strings are externally persisted in cookies or headers, with the raw value and signature delimiter in one string.

## Dependencies and integration points
Used by `AuthenticationFilter` and tests for cookie signing. Depends on JCE `Mac`, `SecretKeySpec`, Commons Codec Base64/StringUtils, and `SignerSecretProvider`.

## Risks and test signals
The delimiter is searched with `lastIndexOf`, so raw values can contain earlier `&s=` fragments. Null provider secrets can fail at sign time. Signature error messages include the full signed text for missing signatures. Tests should cover current/previous secret verification, tampering, delimiter collisions, empty input, null provider output, constant-time comparison behavior, and algorithm availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/Signer.java -->
