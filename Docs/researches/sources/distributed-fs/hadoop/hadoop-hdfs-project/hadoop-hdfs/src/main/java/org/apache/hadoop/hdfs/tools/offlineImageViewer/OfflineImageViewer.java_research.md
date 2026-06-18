## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/OfflineImageViewer.java

Purpose: `OfflineImageViewer` is the legacy `hdfs oiv_legacy` command for old binary fsimage formats. It selects a legacy `ImageVisitor`, reads the image version, and delegates parsing to `ImageLoaderCurrent` through the loader factory.

Important APIs and control flow: the constructor stores input file, processor, and `skipBlocks`. `go()` opens a `PositionTrackingInputStream`, wraps it in `DataInputStream`, reads the version with `findImageVersion` using mark/reset, obtains an `ImageLoader`, and invokes `loadImage`. On failure it logs the byte offset before cleanup. `main` parses CLI options, validates delimiter usage, selects `Indented`, `XML`, `Delimited`, `FileDistribution`, `NameDistribution`, or default `Ls`, and forces block enumeration for processors that need file sizes.

State, persistence, and dependencies: state is the selected input path, visitor, and skip-block flag. Output is visitor-owned. Dependencies include Commons CLI, `PositionTrackingInputStream`, `ImageLoader`, visitor classes, and Hadoop `IOUtils`.

Integration points: legacy companion to the PB `OfflineImageViewerPB`; useful for older layout versions not handled by PB tools.

Risks and test signals: tests should cover CLI parsing, delimiter validation, default processor, skip-block override, unsupported versions, EOF handling, and failure offset logging. `findImageVersion` assumes the buffered stream supports mark/reset, which current construction satisfies. Main catches IO errors and prints messages rather than returning structured status.
