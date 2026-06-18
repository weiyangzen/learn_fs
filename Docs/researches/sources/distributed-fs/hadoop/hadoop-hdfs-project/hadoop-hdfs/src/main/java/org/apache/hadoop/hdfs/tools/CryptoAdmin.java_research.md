<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/CryptoAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/CryptoAdmin.java

## Purpose

`CryptoAdmin` implements the `hdfs crypto` CLI for HDFS encryption zones, file encryption information, trash provisioning, and zone re-encryption commands/status.

## Important APIs and types

The tool extends `Configured` and implements `Tool`. Commands are `-createZone`, `-listZones`, `-provisionTrash`, `-getFileEncryptionInfo`, `-reencryptZone`, and `-listReencryptionStatus`. It uses `HdfsAdmin`, `CreateEncryptionZoneFlag.PROVISION_TRASH`, `EncryptionZone`, `FileEncryptionInfo`, `ReencryptAction`, `ZoneReencryptionStatus`, `RemoteIterator`, `TableListing`, and `Time`.

## Control flow

`run` dispatches to a command and reports unknown commands/argument exceptions. `-createZone` requires `-path` and `-keyName`, creates an `HdfsAdmin` for the path URI, and provisions trash while creating the zone. `-listZones` lists all zones from the default filesystem. `-getFileEncryptionInfo` fetches and prints stable file encryption info. `-provisionTrash` provisions an encryption-zone trash directory. `-reencryptZone` requires exactly one of `-start` or `-cancel` plus `-path`, then submits the action. `-listReencryptionStatus` prints status rows and emits a warning when failures are present.

## State and persistence behavior

The CLI mutates persistent NameNode encryption-zone metadata, trash directories, and re-encryption work queues. It also reads encryption info and re-encryption status.

## Dependencies and integration points

It integrates with HDFS encryption-zone administration through `HdfsAdmin`, Hadoop key-provider-backed encryption metadata, NameNode re-encryption status, CLI option parsing, and generic tool execution.

## Risks and test signals

`-getFileEncryptionInfo` and `-provisionTrash` do not explicitly reject missing `-path` before constructing `new Path(path)`, so missing path may surface as an argument exception rather than command-specific help. `prettifyException` assumes a non-null localized message. Tests should cover all commands, missing/extra arguments, create-zone trash provisioning, list output, null encryption info, re-encryption start/cancel exclusivity, failure warning output, and exit codes for NameNode errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/CryptoAdmin.java -->
