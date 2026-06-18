# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AWSRequestAnalyzer.java

## Purpose
`AWSRequestAnalyzer` converts AWS SDK S3 request objects into compact audit information: statistic verb, mutating/read flag, key or prefix, and approximate size/count.

## Important APIs and control flow
`analyze(SdkRequest)` uses an ordered `instanceof` chain for common S3 requests: MPU abort/complete/start/list/part, object delete/bulk delete/get/head/put, bucket-location probes, and list v1/v2. Unknown requests are treated as mutating with the Java class name. `isRequestNotAlwaysInSpan()` identifies SDK-generated or dependency-generated requests that may not be in a normal S3A span. `isRequestAuditedOutsideOfCurrentSpan()` checks AAL execution attributes. `isRequestMultipartIO()` identifies requests to reject when MPU is disabled. `RequestInfo` exposes verb, mutating flag, key, size, and string formatting.

## State, dependencies, and integration
Instances are stateless. The analyzer depends on AWS SDK S3 request classes, S3A statistics names, and AAL execution attribute constants. It is used by audit managers and logging auditors for log messages and policy decisions.

## Risks and test signals
The `GetObject` range-size parsing returns `end - start`, which may not match inclusive HTTP byte ranges. Unknown requests default to mutating, which is conservative but may overstate risk. Tests should cover every supported request type, empty bulk deletes, multipart predicates, AAL attribute detection, and malformed range headers.
