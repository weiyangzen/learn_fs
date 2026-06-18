# sources/distributed-fs/seaweedfs/weed/s3api/credential_iam_errors.go

Purpose: maps credential-store errors to AWS IAM error code strings for embedded S3 IAM handling and standalone IAM API consistency.

Important API: `CredentialErrToIamErrCode(err error) string`.

Control flow: `errors.Is` maps user-already-exists to `EntityAlreadyExists`, user/access-key not found to `NoSuchEntity`, and everything else to `ServiceFailure`.

State and persistence: pure error translation with no state.

Dependencies and integration points: AWS IAM SDK error constants and SeaweedFS credential sentinel errors.

Risks and test signals: defaulting to service failure prevents unexpected backend errors from becoming misleading client errors. New credential sentinel errors need explicit mapping if they require specific IAM responses.
