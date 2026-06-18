# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/backend_test.go

Purpose: validates OSS/S3 backend config JSON conversion and backend config parsing.

Important APIs under test: `rawMetaBackendCfg`, `rawBlobBackendCfg`, `backendType`, `ParseBackendConfigString`, and `ParseBackendConfig`.

Control flow and state: tests instantiate S3 and OSS configs, create backend clients from raw configs, unmarshal JSON to assert prefix and credential fields, verify empty OSS fields still marshal, and exercise supported/unsupported parsing paths.

Dependencies and integration points: shared backend factory, JSON decoding, and testify require.

Risks and test signals: tests cover config shape but not real cloud authentication or upload behavior. Empty-field tests confirm local validation is permissive.
