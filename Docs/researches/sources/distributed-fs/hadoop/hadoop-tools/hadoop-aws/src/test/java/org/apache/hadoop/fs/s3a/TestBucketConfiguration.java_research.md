# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestBucketConfiguration.java

## Purpose

Unit tests for per-bucket S3A configuration propagation, credential-provider path patching, and deprecated encryption option resolution.

## Important APIs, Types, and Functions

Tests exercise `S3AUtils.setBucketOption()`, `clearBucketOption()`, `propagateBucketOptions()`, `patchSecurityCredentialProviders()`, `getEncryptionAlgorithm()`, and `buildEncryptionSecrets()`. They also use Hadoop credential-provider APIs to store JCEKS-backed encryption keys.

## Control Flow

`setup()` forces S3A deprecation wiring. Propagation tests build minimal configurations, set bucket-specific values, propagate for a target bucket, and assert base keys, property sources, resolution of `${fs.s3a.base}`, multiple bucket isolation, and skipped unmodifiable keys. Credential tests combine base and S3A-specific provider paths. Encryption tests verify older per-bucket server-side encryption keys override newer global keys, including through a local Java keystore provider.

## State, Dependencies, and Integration Points

State is confined to `Configuration` instances and a temporary JCEKS file. It integrates S3A bucket-option mapping, Hadoop configuration interpolation, credential provider path merging, deprecation mappings, and encryption-secret construction.

## Risks and Test Signals

Bucket option rewriting is fragile because it must avoid loops and must not alter unmodifiable filesystem implementation keys. The strongest signals are exact option values, property source traces, merged credential provider path order, and encryption algorithm/key resolution from both XML-style config and JCEKS secrets.
