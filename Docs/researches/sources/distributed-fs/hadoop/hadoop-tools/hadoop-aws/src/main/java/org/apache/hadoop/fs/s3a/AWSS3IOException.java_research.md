# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSS3IOException.java

Purpose: public evolving wrapper for S3-specific `S3Exception` instances as Hadoop IOExceptions.

Important APIs/types: extends `AWSServiceIOException`; `getCause()` narrows to `S3Exception`; annotated public/evolving.

Control flow: created during S3A exception translation for S3 service failures not mapped to a more specific subclass.

State and persistence behavior: retains operation and original S3 exception.

Dependencies and integration points: exposes AWS SDK v2 S3 exception details while fitting Hadoop `IOException` contracts.

Risks: public API stability is evolving; callers should avoid depending on implementation-specific message text.

Test signals: translation tests should verify cause narrowing and inherited access to request ID, status code, extended request ID, and error details.
