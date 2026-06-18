# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ACannedACLs.java

Purpose: validates S3A canned ACL configuration is applied to created and renamed objects.

Important APIs/types/functions: extends `AbstractS3ATestBase`; `createConfiguration()` skips unless ACL tests are enabled, disables FS caching, removes `CANNED_ACL`, sets it to `LOG_DELIVERY_WRITE`, and disables out-of-span audit rejection. `assertObjectHasLoggingGrant()` calls AWS SDK `getObjectAcl()` and checks for LogDelivery WRITE grant.

Control flow: test creates a directory, checks directory marker ACL, touches a file, checks file ACL, renames file, and checks renamed object ACL inside an audit span.

State and persistence: creates directory marker and file objects with canned ACLs, then renames a file.

Dependencies and integration: AWS SDK S3 ACL APIs, S3A store context/path-to-key mapping, audit spans, and ACL test enable flag.

Risks: requires ACL permissions and buckets that support ACLs. Directory marker key appends `/` manually, matching S3A marker conventions.

Test signals: integration coverage for canned ACL propagation on mkdir, create, and rename/copy.
