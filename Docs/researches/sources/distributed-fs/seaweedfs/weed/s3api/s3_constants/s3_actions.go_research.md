# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_actions.go

Purpose: defines legacy/coarse SeaweedFS action labels and common S3 internal folder/header constants.

Important APIs and values: coarse actions include `ACTION_READ`, `ACTION_READ_ACP`, `ACTION_WRITE`, `ACTION_WRITE_ACP`, `ACTION_ADMIN`, `ACTION_TAGGING`, `ACTION_LIST`, `ACTION_DELETE_BUCKET`, object-lock/retention/legal-hold actions, and object-lock config actions. Also defines `SeaweedStorageDestinationHeader`, `MultipartUploadsFolder`, `VersionsFolder`, and `FolderMimeType`.

Control flow: no functions.

State and persistence: constants are used in identity action lists and internal object layout names such as `.uploads` and `.versions`.

Dependencies and integration: `s3_action_resolver.go` maps these coarse actions to AWS S3 action strings. Multipart/versioning code uses folder constants.

Risks: coarse actions are less precise than AWS action strings; callers should use `ResolveS3Action` with HTTP context before authorization.

Test signals: resolver and granular security tests cover mappings from these coarse actions.
