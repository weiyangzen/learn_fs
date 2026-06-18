<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ClientManager.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ClientManager.java

## Purpose

`ClientManager` defines the lifecycle and lazy-access contract for S3A AWS SDK clients.

## Important APIs, Types, and Functions

It extends Hadoop `Service` and declares getters for transfer manager, sync S3 client, async client, unencrypted S3 client, and unchecked variants.

## Control Flow

Implementations are expected to create clients lazily, translate checked creation failures to `IOException`, and provide unchecked wrappers where required by callback APIs.

## State and Persistence Behavior

As an interface it has no state. Implementations own client references and service lifecycle.

## Dependencies and Integration Points

It integrates `S3Client`, `S3AsyncClient`, `S3TransferManager`, Hadoop service lifecycle, and CSE/V1 compatibility paths needing an unencrypted client.

## Risks and Edge Cases

Unchecked async getter naming returns `S3Client` in this source, so callers must follow the exact declared contract. Service shutdown must close any clients created lazily.

## Test Signals

Implementation tests should assert lazy creation, repeated getter identity, checked/unchecked error conversion, unencrypted-client behavior, transfer manager creation, and cleanup on service stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ClientManager.java -->
