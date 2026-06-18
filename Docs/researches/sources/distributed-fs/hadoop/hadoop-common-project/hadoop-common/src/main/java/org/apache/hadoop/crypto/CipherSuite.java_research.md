# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/CipherSuite.java`

## Purpose

`CipherSuite` defines supported cipher suite metadata for Hadoop crypto streams and protocol negotiation.

## Important APIs and Types

Constants are `UNKNOWN`, `AES_CTR_NOPADDING`, and `SM4_CTR_NOPADDING`. Each stores a JCE-style name and algorithm block size. Methods include `setUnknownValue`, `getUnknownValue`, `getName`, `getAlgorithmBlockSize`, `convert(String)`, `getConfigSuffix`, and `toString`.

## Control Flow

`convert` linearly scans enum values and matches by exact `getName`, throwing `IllegalArgumentException` when no name matches. `getConfigSuffix` splits the JCE-style name on `/`, lowercases each part through Hadoop `StringUtils`, and prepends dots to build keys such as `.aes.ctr.nopadding`.

## State and Persistence

Enum instances are mostly immutable except for `unknownValue`, which can be set on an enum constant. That mutability is used when preserving unknown wire values during protocol decoding.

## Dependencies and Integration Points

`CryptoCodec`, `CryptoStreamUtils`, `JceAesCtrCryptoCodec`, and stream classes depend on suite name and block size. Configuration keys for codec class discovery are derived from `getConfigSuffix`.

## Risks

`UNKNOWN.getUnknownValue()` unboxes an `Integer` and can throw `NullPointerException` if called before `setUnknownValue`. `convert` is case-sensitive and name-based, not enum-name-based. Adding suites requires configuration defaults, codec implementations, and `CryptoStreamUtils.checkCodec` updates if streams should accept them.

## Test Signals

Tests should cover name conversion success/failure, config suffix construction, unknown value preservation, block-size expectations, and behavior when new suite constants are added.
