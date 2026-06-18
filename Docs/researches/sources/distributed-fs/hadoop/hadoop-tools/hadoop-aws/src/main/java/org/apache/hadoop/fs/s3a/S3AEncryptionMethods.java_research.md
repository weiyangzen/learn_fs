# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AEncryptionMethods.java

## Purpose

`S3AEncryptionMethods` centralizes the encryption algorithm names accepted by S3A configuration and records whether each method is server-side and whether it requires a secret in the encryption key property. It gives the rest of S3A a typed enum instead of stringly-typed encryption checks.

## Important APIs, Types, and Functions

- Enum values:
  - `NONE("", false, false)`
  - `SSE_S3("AES256", true, false)`
  - `SSE_KMS("SSE-KMS", true, false)`
  - `SSE_C("SSE-C", true, true)`
  - `CSE_KMS("CSE-KMS", false, true)`
  - `CSE_CUSTOM("CSE-CUSTOM", false, true)`
  - `DSSE_KMS("DSSE-KMS", true, false)`
- `UNKNOWN_ALGORITHM`: stable error prefix used by tests and callers.
- `getMethod()`: returns the configuration/S3 algorithm string.
- `isServerSide()`: distinguishes server-side encryption from client-side encryption.
- `requiresSecret()`: indicates whether a separate secret/key must be looked up.
- `static getMethod(String name)`: parses a case-insensitive method string, treats blank values as `NONE`, and throws `IOException` for unknown algorithms.

## Control Flow

Parsing is linear over enum values. Blank or whitespace-only input returns `NONE` through `StringUtils.isBlank()`. Otherwise the method string is compared case-insensitively against each enum's configured method value. Unknown values fail fast with `IOException`.

There is no mutation. Each enum instance stores immutable metadata supplied by the constructor.

## State and Persistence Behavior

The enum has no persistent state. It influences later persistence behavior indirectly: server-side values affect S3 request headers and client-side values affect encrypted client setup and upload handling. `requiresSecret()` is used by secret/delegation-token code to decide whether an encryption key must be present.

## Dependencies and Integration Points

- `S3AUtils.getEncryptionAlgorithm()` calls `S3AEncryptionMethods.getMethod()` while loading bucket-specific configuration and validating key requirements.
- `S3AFileSystem` uses the parsed algorithm to decide whether client-side encryption is enabled.
- `RequestFactory` exposes server-side encryption algorithm settings for request construction.
- `EncryptionSecrets` serializes/deserializes method strings for delegation token support.
- `EncryptionSecretOperations` validates SSE-C, SSE-KMS, and DSSE-KMS secret/context requirements.
- `S3ObjectAttributes` carries the server-side encryption method in object metadata.

## Risks and Edge Cases

- The parser accepts only `getMethod()` strings, not enum constant names. For example, callers must pass `SSE-KMS`, not necessarily `SSE_KMS`.
- Blank input silently maps to `NONE`; this is convenient for unset configuration but can hide accidental whitespace-only values.
- Adding a new encryption method requires updating downstream validation, request construction, secret handling, and tests, not just this enum.
- `requiresSecret()` is true for SSE-C and client-side encryption modes but false for KMS modes, where a KMS key id may be optional or configured separately depending on AWS behavior and S3A validation.

## Test Signals

Tests refer to `UNKNOWN_ALGORITHM` and exercise encryption parsing through `S3AUtils`, `EncryptionSecrets`, client-side encryption integration tests, and request factory setup. Useful regression coverage includes blank input, case-insensitive parsing, unknown algorithm error text, `isServerSide()` for CSE versus SSE methods, and `requiresSecret()` for SSE-C/CSE modes.
