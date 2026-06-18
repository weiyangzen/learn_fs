## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/FileDistributionCalculator.java

Purpose: `FileDistributionCalculator` computes file-size distribution directly from a protobuf fsimage without using the legacy visitor pipeline. It backs `OfflineImageViewerPB -p FileDistribution`.

Important APIs and control flow: the constructor applies defaults for max size and interval, validates the number of buckets against `MAX_INTERVALS`, and allocates an integer distribution array. `visit(RandomAccessFile)` validates fsimage format, loads the summary, seeks to the `INODE` section, wraps it for compression and length limiting, then calls `run` and `output`. `run` parses the inode-section header and each delimited inode, counting files, directories, blocks, total replicated space, max file size, and bucket counts based on summed block bytes. `output` writes either raw byte bucket starts or human-readable ranges plus totals.

State, persistence, and dependencies: state is counters and the distribution array. Dependencies include protobuf fsimage classes, `FSImageUtil`, `LimitInputStream`, `BlockProto`, `StringUtils.byteDesc`, and `Configuration`.

Integration points: selected by `OfflineImageViewerPB` and writes to the command output stream.

Risks and test signals: tests should cover default values, bucket boundaries, files larger than max size, max-size not divisible by step, compressed images, empty images, and OOM-prevention validation. The progress message every 1,048,576 inodes goes to the same output stream and may affect machine parsing.
