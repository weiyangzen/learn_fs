<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/select/SelectConstants.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/select/SelectConstants.java

Purpose: constant holder for legacy S3 Select configuration keys, capability strings, and CSV/JSON option values, while declaring S3 Select unsupported.

Important APIs/types/functions: private constructor prevents instantiation. `SELECT_UNSUPPORTED` is the user-facing unsupported message. Constants cover `fs.s3a.select.*`, SQL, capability, enablement, input/output format, compression, CSV input/output delimiters, quote settings, header options, and error SQL inclusion.

Control flow: no methods. Other code can reference constants for compatibility, config parsing, or unsupported command errors.

State/persistence: static constants only.

Dependencies/integration: used by `S3GuardTool` to reject `select` command with `EXIT_UNSUPPORTED_VERSION`, and by any remaining tests/config compatibility code.

Risks/test signals: stale constants may preserve compatibility but should not imply feature support. Tests should assert unsupported command behavior and constant names expected by existing configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/select/SelectConstants.java -->
