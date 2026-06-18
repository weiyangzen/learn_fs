<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEMaterials.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEMaterials.java

## Purpose

`CSEMaterials` is a mutable value holder for client-side encryption material selection.

## Important APIs, Types, and Functions

The nested `CSEKeyType` enum distinguishes `KMS` and `CUSTOM`. Fluent setters include `withKmsKeyId()`, `withCustomCryptographicClassName()`, `withConf()`, and `withCSEKeyType()`. Getters expose KMS key id, custom keyring class, configuration, and selected key type.

## Control Flow

Callers build an instance by chaining setters after `CSEUtils` determines the configured encryption method. `EncryptionS3ClientFactory` later reads the selected key type to build KMS or custom keyrings.

## State and Persistence Behavior

The object stores mutable fields in memory only. It does not clone the Hadoop `Configuration`, so callers share the same configuration reference.

## Dependencies and Integration Points

It depends on Hadoop `Configuration` and integrates with `CSEUtils` and `EncryptionS3ClientFactory`.

## Risks and Edge Cases

Fields can be left unset if callers skip validation, so downstream factory code must still check required fields. Mutability makes reuse across filesystems risky if a caller changes fields after client creation starts.

## Test Signals

Tests should cover fluent method chaining, both key types, retention of configuration references, and downstream rejection of missing custom class or KMS key where required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEMaterials.java -->
