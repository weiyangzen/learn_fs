# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/S3LogVerbs.java

## Purpose
`S3LogVerbs` names common operation strings seen in S3 server access logs.

## Important APIs and control flow
The final class exposes constants for delete, copy, bulk delete, get, head, ACL/logging/tagging policy operations, list, multipart start/part/complete/list/abort, put, public-access-block, and lifecycle expiration. It has no runtime behavior.

## State, dependencies, and integration
There is no state. These constants support audit/log parsing code and tests that compare parsed S3 log verbs without embedding string literals.

## Risks and test signals
AWS may add or rename log operation strings. Tests should check constants used in parser/audit tests match expected S3 log samples.
