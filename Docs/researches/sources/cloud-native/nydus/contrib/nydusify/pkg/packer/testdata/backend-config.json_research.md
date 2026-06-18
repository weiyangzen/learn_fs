# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/testdata/backend-config.json

Purpose: test fixture containing an OSS backend configuration.

Important fields: `endpoint`, `access_key_id`, `access_key_secret`, `bucket_name`, `meta_prefix`, and `blob_prefix`.

Control flow and state: parsed by packer pusher tests through `ParseBackendConfig("oss", ...)` and expected to produce an `OssBackendConfig` with metadata prefix `test/` and empty blob prefix.

Dependencies and integration points: packer backend config parser and OSS backend config raw JSON generation.

Risks and test signals: contains placeholder credentials and should stay test-only. It validates field names used by user-supplied backend config files.
