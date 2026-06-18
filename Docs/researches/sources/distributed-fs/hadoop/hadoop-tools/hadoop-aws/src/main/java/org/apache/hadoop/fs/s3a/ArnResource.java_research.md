# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/ArnResource.java

Purpose: immutable representation of an S3 ARN-backed resource, currently access points and outposts access points, with endpoint derivation.

Important APIs/types: private fields hold name, owner account ID, region, full ARN, partition, and `accessPointRegionKey`. Getters expose name, account, region, full ARN, and endpoint. Static `accessPointFromArn(String)` parses via AWS SDK `Arn.fromString` and validates region, account ID, and resource string. `getEndpoint()` chooses `s3-accesspoint.%s.amazonaws.com` or `s3-outposts.%s.amazonaws.com` based on `fullArn.contains("s3-outposts")`.

Control flow: parse ARN, validate required fields, extract resource name from `parsed.resource().resource()`, and construct `ArnResource`. Endpoint generation is lazy through getter.

State and persistence behavior: immutable in-memory value object; no persistence.

Dependencies and integration points: depends on AWS SDK ARN parser and S3A access point configuration. It helps S3A convert access point ARN inputs into resource metadata and endpoints.

Risks: endpoint formats ignore partition-specific DNS suffixes even though partition is stored; comments imply AWS SDK endpoint handling elsewhere may use `accessPointRegionKey`, but that field has no getter in this file. `contains("s3-outposts")` is a coarse classifier.

Test signals: tests should cover malformed ARNs, missing region/account/resource, normal access point endpoints, outposts endpoints, and partition variants such as `aws-cn`/`aws-us-gov`.
