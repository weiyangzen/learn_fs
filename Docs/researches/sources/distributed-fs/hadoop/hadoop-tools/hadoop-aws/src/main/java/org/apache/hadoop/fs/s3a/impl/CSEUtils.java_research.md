<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEUtils.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEUtils.java

## Purpose

`CSEUtils` provides helpers for S3 client-side encryption detection, encrypted object length calculation, and material construction from configuration.

## Important APIs, Types, and Functions

Key methods are `isCSEEnabled(String)`, `isObjectEncrypted(S3AStore,String)`, `getUnencryptedObjectLength(...)`, and `getClientSideEncryptionMaterials(Configuration,String,S3AEncryptionMethods)`.

## Control Flow

Encryption is detected by configured method or by object metadata containing the crypto CEK algorithm header. Length calculation returns raw content length for unencrypted objects, uses `x-amz-unencrypted-content-length` metadata when present, and otherwise performs a ranged GET of the final CSE padding block to derive plaintext length. Material construction selects KMS key id from bucket-aware config for `CSE_KMS` or a custom keyring class for `CSE_CUSTOM`.

## State and Persistence Behavior

The utility is stateless. It issues HEAD and range GET calls through `S3AStore` and closes streams used for length probing.

## Dependencies and Integration Points

It depends on S3A encryption constants, AWS metadata headers, `S3AStore.headObject()`, `getRangedS3Object()`, Hadoop configuration helpers, and `CSEMaterials`.

## Risks and Edge Cases

Length derivation has several failure modes: absent metadata, short encrypted objects, parsing errors, and range GET behavior against non-AWS stores. `isObjectEncrypted()` performs an extra HEAD even if a caller already has metadata.

## Test Signals

Cover CSE_KMS/CSE_CUSTOM detection, unencrypted object fast path, metadata length parsing, missing metadata fallback, final-block range reads, invalid metadata values, custom class configuration, and bucket-specific KMS key lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEUtils.java -->
