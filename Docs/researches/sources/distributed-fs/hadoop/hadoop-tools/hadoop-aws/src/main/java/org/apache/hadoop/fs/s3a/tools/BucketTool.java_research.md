<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/BucketTool.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/BucketTool.java

Purpose: S3A administrative CLI subcommand for bucket operations, currently focused on creating buckets including S3 Express directory buckets.

Important APIs/types/functions: extends `S3GuardTool`; command name `bucket`; supports `-create`, `-region`, `-endpoint`, and `-zone`. `run()` parses exactly one S3A URL, validates scheme, requires `-create`, strips bucket-specific overrides, disables bucket probe and out-of-span audit rejection for creation, propagates endpoint/region, initializes an S3A filesystem, builds `CreateBucketConfiguration`, handles S3 Express zone/directory bucket settings, gets an AWS `S3Client`, and calls `createBucket()` through `Invoker.once()`. `removeBucketOverrides()` unsets bucket override keys for supplied global options.

Control flow: CLI parse -> validate options -> prepare configuration to avoid probing nonexistent bucket -> instantiate filesystem -> build request based on S3 Express capability -> create bucket -> close filesystem.

State/persistence: mutates the provided `Configuration` by unsetting/setting keys. Remote side effect is creation of an S3 bucket. No local persistence.

Dependencies/integration: AWS SDK S3 bucket creation models, S3A filesystem internals, S3 Express helpers, audit constants, network endpoint checks, and `DurationInfo`.

Risks/test signals: bucket creation is remote and irreversible without cleanup; probe disabling is required for nonexistent buckets; S3 Express zone rules are strict. Tests should cover URL scheme validation, missing create flag, override removal, probe failure mapping, S3 Express zone required/forbidden cases, and request fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/BucketTool.java -->
