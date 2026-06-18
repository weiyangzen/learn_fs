## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/ImageLoaderCurrent.java

Purpose: `ImageLoaderCurrent` is the legacy binary fsimage parser for layout versions `-16` through `-51`. It decodes the non-protobuf fsimage format and emits `ImageVisitor` events for metadata, inodes, snapshots, blocks, permissions, delegation tokens, and cache state.

Important APIs and control flow: `canLoadVersion` checks a static version array. `loadImage` starts the visitor, reads the layout version and optional layout flags, emits namespace metadata, conditionally reads sequential block id, transaction id, inode id, snapshot counters, and compression metadata, then wraps the stream if compressed. It delegates to `processINodes`, clears snapshot reference tracking maps, processes under-construction inodes, delegation tokens, and cache manager state, then closes the top-level element and calls `finish` or `finishAbnormally`.

State, persistence, and dependencies: parser state includes `imageVersion`, `subtreeMap` for referenced snapshot subtrees, `dirNodeMap` for directory id to path, and a date formatter. It reads persistent fsimage bytes but writes only visitor output. Dependencies include NameNode layout feature flags, `FSImageSerialization`, compression codecs, `DelegationTokenIdentifier`, `DelegationKey`, permissions, and HDFS constants.

Integration points: selected by `ImageLoader.LoaderFactory` and driven by legacy `OfflineImageViewer`.

Risks and test signals: this file is highly layout-sensitive. Tests should cover each feature gate, compressed images, block skipping, local-name versus full-path layouts, snapshot diffs and references, symlinks, directories, files under construction, delegation tokens, and cache state. Skipping blocks uses a fixed 24 bytes per block assumption; layout changes around block serialization must be guarded by compatibility tests.
