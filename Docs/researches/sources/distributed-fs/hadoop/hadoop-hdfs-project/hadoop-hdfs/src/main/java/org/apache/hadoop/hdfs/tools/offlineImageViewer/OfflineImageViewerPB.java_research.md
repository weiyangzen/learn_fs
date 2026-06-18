## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/OfflineImageViewerPB.java

Purpose: `OfflineImageViewerPB` is the primary `hdfs oiv` command for protobuf fsimages. It supports XML dump, reverse XML reconstruction, file distribution, WebHDFS-like browsing, delimited text, and corruption detection.

Important APIs and control flow: `buildOptions()` defines input, optional output, processor, Web address, file-distribution parameters, delimiter, storage-policy and erasure-coding flags, temp directory, and thread count. `run` handles no-arg/help cases, parses options, defaults processor to `Web` and output to stdout, creates a `Configuration`, opens a `PrintStream` when needed, then dispatches on uppercase processor. Each case instantiates the appropriate worker: `FileDistributionCalculator`, `PBImageXmlWriter`, `OfflineImageReconstructor`, `WebImageViewer`, `PBImageDelimitedTextWriter`, or `PBImageCorruptionDetector`. It checks `PrintStream.checkError()` before returning success.

State, persistence, and dependencies: the class is stateless. Persistence includes output files, optional reconstructed image `.md5`, web server lifecycle, and temp paths owned by selected processors. Dependencies include Commons CLI, Hadoop `Configuration`, `NetUtils`, `ExitUtil`, and PB image processors.

Integration points: invoked by the Hadoop CLI and by tests through `run`.

Risks and test signals: tests should cover each processor, stdout output, invalid processor, help exit codes, parse failures, disk-full detection via `checkError`, and cleanup of closeable processors. `ReverseXML` catches exceptions and calls `ExitUtil.terminate(1)`, which needs test harness handling. Web mode runs until the viewer stops.
