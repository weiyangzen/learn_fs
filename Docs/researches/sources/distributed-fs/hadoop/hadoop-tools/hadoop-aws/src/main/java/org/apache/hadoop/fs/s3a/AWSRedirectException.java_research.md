# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSRedirectException.java

Purpose: typed service IOException for redirect responses that reach S3A callers.

Important APIs/types: extends `AWSServiceIOException` and only defines an operation/cause constructor.

Control flow: exception translation constructs this when redirect handling was not resolved by the SDK/client configuration. No local recovery logic exists.

State and persistence behavior: standard wrapped exception state only.

Dependencies and integration points: connects endpoint/region misconfiguration handling with callers that need a Hadoop `IOException`.

Risks: redirects surfacing to users are generally configuration problems; retrying without endpoint/region changes may loop or fail repeatedly.

Test signals: endpoint-region tests should assert redirect responses translate to this type with AWS request details preserved.
