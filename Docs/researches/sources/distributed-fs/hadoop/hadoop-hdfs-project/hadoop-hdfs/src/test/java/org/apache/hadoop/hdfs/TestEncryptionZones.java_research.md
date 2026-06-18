# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptionZones.java

## Purpose
Provides broad integration coverage for HDFS transparent encryption zones. It covers zone creation/listing/querying, permissions, key-provider discovery, file encryption info, read/write correctness, snapshots, trash, raw paths, WebHDFS behavior, fsck/OIV compatibility, delegation tokens, and race handling during encrypted file creation.

## Important APIs and Types
Primary APIs include `HdfsAdmin.createEncryptionZone`, `listEncryptionZones`, `getEncryptionZoneForPath`, `provisionEncryptionZoneTrash`, `DistributedFileSystem.getEZForPath`, `CryptoAdmin`, `FsShell`, `WebHdfsFileSystem`, `DFSClient.getKeyProviderUri`, `addDelegationTokens`, `getLocatedBlocks`, snapshot APIs, and `DFSOutputStream.SUPPORTED_CRYPTO_VERSIONS`. Important types include `EncryptionZone`, `FileEncryptionInfo`, `KeyProvider`, `Credentials`, `Token`, `EncryptionFaultInjector`, `FsServerDefaults`, `CryptoInputStream`, `PBImageXmlWriter`, `DFSck`, and `SnapshotDiffReport`.

## Control Flow
`setup()` creates a JKS key provider, starts a one-DataNode cluster, installs the provider into the client, enables a small listing batch size, and creates `test_key`. Tests then exercise feature clusters: basic create/list validation and namespace persistence; root and fully qualified paths; non-superuser list/get access; rename constraints across or within zones; encrypted reads/writes before and after key roll; WebHDFS reads/appends and redirect behavior; cipher/protocol negotiation failure and success; missing provider errors; `FileStatus.isEncrypted`; snapshots and snapshot diffs; symlink and concat restrictions; fsck/OIV XML parsing; root/relative/non-existent path handling; trash roots for nested/root zones; provider URI lookup from credentials, server defaults, and ignore flags; and raw reserved path writes. `testStartFileRetry` uses `EncryptionFaultInjector` and latches to simulate races while generating EDEKs.

## State, Persistence, Dependencies, Integration
Persistent state includes encryption-zone xattrs/metadata, fsimage/edit-log records, key versions, encrypted data encryption keys, snapshots, trash directories, and delegation-token credentials. Dependencies include JKS key provider plumbing, NameNode encryption-zone manager, client/server defaults, WebHDFS HTTP redirects, snapshot manager, FsShell, and offline image viewer. The test integrates public admin APIs with raw DFS client metadata and shell/tool behavior.

## Risks and Test Signals
Signals are numerous: zone counts and metrics, expected authorization failures, file byte equality despite encrypted storage, different EDEKs after key roll, snapshot-specific zone metadata, healthy fsck output, parseable OIV XML, correct trash-root placement, KMS URI fallback behavior, WebHDFS raw-vs-decrypted stream checks, and retry count behavior during zone races. Risks are broad setup complexity, mutable static crypto-version fields, timing in concurrency tests, and reliance on exact exception/log messages.
