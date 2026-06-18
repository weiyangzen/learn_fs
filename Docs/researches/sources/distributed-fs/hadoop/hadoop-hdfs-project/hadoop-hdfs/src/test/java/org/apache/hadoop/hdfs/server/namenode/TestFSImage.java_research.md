# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSImage.java

## Purpose
`TestFSImage` validates fsimage save/load behavior across ordinary files, under-construction files, compression, legacy image compatibility, erasure coding, block maps, policy persistence, parallel fsimage loading, and snapshot/name-cache rebuilds.

## Important APIs, Types, And Functions
The class uses `MiniDFSCluster`, `FSNamesystem`, `FSImage`, `FSImageSerialization`, `FSImageFormat.Loader`, `FSImageFormatProtobuf`, `FSImageTestUtil`, `DistributedFileSystem`, `SecondaryNameNode`, `MD5FileUtils`, `ErasureCodingPolicyManager`, `SystemErasureCodingPolicies`, `BlockInfoStriped`, `BlockInfoContiguous`, `SnapshotTestHelper`, and `DFSOutputStream.hsync`. Helpers include `testPersistHelper`, `testSaveAndLoadStripedINodeFile`, `testChangeErasureCodingPolicyState`, `isPolicyEnabledInFsImage`, `createAndLoadParallelFSImage`, `getSubSectionsOfName`, and `ensureSubSectionsAlignWithParent`.

## Control Flow
Basic persistence tests create empty and under-construction files, save the namespace, restart, and validate directory presence, file size, block under-construction state, and lease tracking. Compression tests rerun persistence with default, gzip, bzip2, and native lz4 codecs. Striped inode tests serialize and deserialize normal and under-construction striped inode files. Checkpoint tests validate missing checkpoint edits-dir errors, deletion of stale `fsimage.ckpt_*`, and fsimage MD5 sidecar correctness. Legacy and block tests load a Hadoop 2.7 image with zero block size, persist/reload block groups under multiple EC policies, and detect non-EC blocks with striped IDs in files, under-construction files, and snapshots.

## State And Persistence Behavior
The file is centered on fsimage persistence. It creates checkpoints through safe mode and `saveNamespace`, restarts NameNodes without formatting, and inspects both client-visible paths and internal inode/block state. EC policy tests verify policy definitions and enabled/disabled/removed states in `ErasureCodingPolicyManager` and the persisted policy list. Parallel fsimage tests inspect protobuf file-summary sections to ensure generated inode and directory subsections cover contiguous byte ranges and align with parent sections. The async block-map/name-cache test compares pre- and post-restart namespace tree dumps after snapshots and renames.

## Dependencies And Integration Points
This suite integrates fsimage serialization with HDFS client operations, NameNode lease manager, block manager, EC policy manager, secondary checkpointing, compression codecs, native-code availability, old test-cache images, protobuf section metadata, and snapshot tree utilities. Some tests depend on enough datanodes for EC group sizes.

## Risks And Test Signals
Risks include losing under-construction file state, broken compression handling, stale checkpoint files accumulating, digest mismatches, legacy images failing upgrade, EC block groups or policy IDs being serialized incorrectly, non-EC striped-ID flags being missed, default protobuf block type changing, parallel fsimage sections overlapping or leaving gaps, and async restart rebuilding a different namespace tree. Test signals are file existence, lease presence, exact block metadata, MD5 equality, policy state assertions, readable file bytes, section counts and offsets, and tree-dump comparison.
