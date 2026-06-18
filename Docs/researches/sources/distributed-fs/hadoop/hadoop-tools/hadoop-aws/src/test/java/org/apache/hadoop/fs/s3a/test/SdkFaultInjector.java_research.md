<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/SdkFaultInjector.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/SdkFaultInjector.java


## Purpose
AWS SDK v2 ExecutionInterceptor used by tests to inject post-success HTTP failures into selected S3 requests.


## Important APIs, Types, and Functions
SdkFaultInjector exposes static evaluators/actions/counters, request predicates such as isGetRequest/isPutRequest/isPartUpload/isMultipartAbort, reset/set methods, modifyHttpResponse(), patchStatusCode(), shouldFail(), and addFaultInjection().


## Control Flow
modifyHttpResponse inspects the SDK context after S3 has responded. If the evaluator matches and the failure count still demands failure, it applies the configured action, normally copying the HTTP response with a configured error status. addFaultInjection wires the interceptor through S3A audit execution interceptors.


## State and Persistence Behavior
State is global static and mutable: failure status, failure count, evaluator, and action. Tests must reset before/after use to avoid cross-test contamination.


## Dependencies and Integration Points
Depends on AWS SDK ExecutionInterceptor/Context/SdkHttpResponse, S3 request classes, S3A audit test support, Configuration, and InternalConstants status codes.


## Risks and Test Signals
Risks are race/cross-test interference from static state and the fact that failures happen after the backend operation succeeded. Signals are powerful for retry, abort, and cleanup tests that need deterministic SDK-layer errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/SdkFaultInjector.java -->
