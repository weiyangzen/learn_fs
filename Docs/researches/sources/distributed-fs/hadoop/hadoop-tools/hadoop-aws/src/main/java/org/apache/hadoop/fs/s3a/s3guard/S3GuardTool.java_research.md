<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3GuardTool.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3GuardTool.java

Purpose: command-line entry point and base class for S3A administrative commands historically under `s3guard`. It now rejects unsupported S3Guard commands while dispatching supported bucket, marker, bucket-info, and multipart upload tools.

Important APIs/types/functions: base `S3GuardTool` handles `CommandFormat`, filesystem binding/unwrapping, age option parsing, IO statistics dumping, formatted errors, and `ExitUtil.ExitException` helpers. Nested `BucketInfo` reports bucket/client/committer/security/marker/capability status and validates requested flags. Nested `Uploads` lists, expects, or aborts multipart uploads, with optional age filters, verbose mode, and force prompt bypass. Static `run(Configuration,String...)` parses generic options, rejects unsupported command names, dispatches subcommands, and cleans up. `main()` maps exceptions to launcher exit codes.

Control flow: CLI parses generic Hadoop options, selects a subcommand, constructs the tool, delegates through `ToolRunner`, then closes resources. `BucketInfo` binds to an S3A FS, probes location/capabilities, prints config and validates requested properties. `Uploads` resolves mode, prompts before abort unless forced, iterates `fs.listUploads(prefix)`, filters by age, optionally aborts through `WriteOperationHelper`, and validates expected counts.

State/persistence: base class holds the bound base filesystem and S3A filesystem until close. Upload abort mode mutates remote S3 multipart upload state. Other modes mainly inspect configuration and remote metadata.

Dependencies/integration: integrates Hadoop `Tool`, `GenericOptionsParser`, `ToolRunner`, S3A filesystem internals, commit constants, delegation tokens, audit spans, AWS multipart uploads, marker/bucket tools, and IO statistics logging.

Risks/test signals: user-facing exit code mapping is important for scripts. Upload abort is destructive and protected only by prompt/force. Tests should cover unsupported commands, wrong filesystem binding, bucket-info validation flags, upload mode mutual exclusion, age filtering, expected count failures, and cleanup on exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/s3guard/S3GuardTool.java -->
