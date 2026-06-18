<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerTool.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerTool.java

Purpose: administrative tool to audit or clean surplus S3 directory markers under a path.

Important APIs/types/functions: extends `S3GuardTool`; supports mutually exclusive `-audit` and `-clean`, `-min`, `-max`, `-limit`, `-out`, and `-verbose`. `run()` parses options, resolves filesystem/path, executes a scan, optionally writes surplus marker paths to a UTF-8 file, and returns/throws based on `ScanResult.finish()`. `execute()` binds S3A FS, qualifies target, verifies existence, creates `MarkerToolOperations`, and calls `scan()`. `ScanResult` and `MarkerPurgeSummary` capture outcomes. `scanDirectoryTree()` lists objects and feeds `DirMarkerTracker`. `purgeMarkers()` shuffles surplus marker keys and bulk-deletes pages. `ScanArgs` and builder support programmatic execution.

Control flow: scan lists objects from a key prefix, retries with trailing slash after certain bad requests, classifies directory statuses as markers and files as files, reports surplus/leaf markers, optionally purges surplus markers, validates min/max marker count for audit, and handles listing limit interruption.

State/persistence: holds output stream, verbosity, store context, and operations during execution. Clean mode mutates remote S3 object state by deleting marker objects. `-out` writes a local file containing surplus marker paths.

Dependencies/integration: `DirMarkerTracker`, S3A `StoreContext`, `S3AFileStatus`, `S3ALocatedFileStatus`, AWS object identifiers, bulk delete settings, retry annotations, and `MarkerToolOperations`.

Risks/test signals: clean mode is destructive; randomized delete order affects deterministic tests unless mocked; min/max defaults make audit fail when any surplus marker is found unless max is raised. Tests should cover option parsing, audit/clean exclusivity, missing/wrong paths, listing fallback with trailing slash, limit interruption, leaf versus surplus classification, output file generation, and paged delete summaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerTool.java -->
