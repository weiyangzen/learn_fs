# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/UploadInfo.java

## Purpose
`UploadInfo` is a small struct pairing an AWS transfer-manager `FileUpload` with the expected upload length.

## Important APIs, Types, and Functions
The constructor stores `FileUpload` and length. Getters are `getFileUpload()` and `getLength()`.

## Control Flow and State
There is no control flow beyond storing the upload handle. `S3AStore.putObject()` returns this object and `waitForUploadCompletion()` consumes it to wait and update completion statistics.

## State and Persistence Behavior
State is an in-memory handle to an active asynchronous upload plus a byte length. Remote persistence is the eventual S3 object created by the upload, managed by AWS transfer manager code.

## Dependencies and Integration Points
Dependency is AWS SDK transfer manager `FileUpload`. It integrates with S3A put/upload completion paths and statistics accounting.

## Risks and Test Signals
Risks include null upload handles, incorrect length causing wrong statistics, and lifetime mismatch where source files/buffers disappear before async upload completion. Tests should verify length propagation, completion stats using length, failed/cancelled upload handling, and null expectations.
