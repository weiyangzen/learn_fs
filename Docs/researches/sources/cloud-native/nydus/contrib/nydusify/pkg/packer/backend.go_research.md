# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/backend.go

Purpose: defines packer backend configuration abstractions for OSS and S3 storage, separating metadata and blob object prefixes.

Important APIs/types/functions: `BackendConfig`, `OssBackendConfig`, `S3BackendConfig`, `rawMetaBackendCfg`, `rawBlobBackendCfg`, and `backendType`.

Control flow: each concrete config converts user-facing fields into JSON expected by the shared backend package. OSS emits simple string maps with `object_prefix` set to meta or blob prefix. S3 emits `backend.S3Config` JSON with endpoint, scheme, credentials, bucket, region, and prefix.

State and persistence: no state beyond config structs. Sensitive access keys are serialized into JSON byte slices for backend initialization and temporary config dumps.

Dependencies and integration points: packer pusher, backend factory, S3/OSS backend implementations, and compactor temp config creation.

Risks and test signals: JSON marshal errors are ignored, though these structs should marshal successfully. Secrets may be written to disk or command arguments by callers. Empty config fields are allowed and may fail only when backend clients initialize or upload.
