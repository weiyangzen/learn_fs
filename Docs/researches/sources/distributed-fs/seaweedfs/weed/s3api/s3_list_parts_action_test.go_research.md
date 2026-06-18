# sources/distributed-fs/seaweedfs/weed/s3api/s3_list_parts_action_test.go

## Purpose
This test file documents and verifies S3 action resolution for multipart `ListParts` requests. It exists to prevent GET requests with an `uploadId` query parameter from being authorized as ordinary `s3:GetObject` reads.

## Important APIs, Types, and Functions
All tests call `ResolveS3Action(req, fallbackAction, bucket, objectKey)`. Test groups are `TestListPartsActionMapping`, `TestListPartsActionMappingSecurityScenarios`, and `TestListPartsActionRealWorldScenarios`.

## Control Flow
Each test builds a minimal `http.Request` with method, URL path, and query values. It passes a fallback S3 action constant and asserts the resolved IAM action string. Cases distinguish plain GET, GET with `uploadId`, GET with `versionId`, GET ACL, POST with `uploads`, multipart upload workflow steps, and multiple realistic upload ID formats.

## State and Persistence Behavior
The tests use no persistent state. Requests are constructed in memory and there is no server, filer, IAM manager, or object metadata.

## Dependencies and Integration Points
The file depends on `ResolveS3Action` from the S3 authorization layer and `s3_constants` action constants. It protects integration with IAM policy evaluation because the resolved action is sent to `integration.ActionRequest.Action`.

## Risks and Edge Cases
The test confirms the presence of `uploadId` changes GET semantics, including with additional multipart pagination parameters. It does not test duplicate query parameters, case variations in `uploadId`, or actual handler authorization with a policy engine. Since AWS query names are case-sensitive, that is likely acceptable.

## Test Signals
Passing tests signal that `GET ?uploadId=...` maps to `s3:ListMultipartUploadParts`, plain GET maps to `s3:GetObject`, versioned GET maps to `s3:GetObjectVersion`, ACL GET maps to `s3:GetObjectAcl`, and multipart create/upload/complete/list steps remain distinct for fine-grained permissions.
