# sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_static_config_test.go

Purpose: Tests the distinction between advanced IAM config files with no inline identities and traditional static S3 credential files with identities.

Important APIs, types, and functions: Exercises `loadS3ApiConfigurationFromFile`, `IsStaticConfig`, `onIamConfigChange`, `LoadS3ApiConfigurationFromCredentialManager`, and test helpers `writeTempIamConfig` and `isStaticName`.

Control flow and state: `TestIamConfigWithoutIdentitiesIsNotStatic` loads an STS-only JSON file, creates a dynamic user in the memory credential manager, simulates an `/etc/iam/identities` event, and expects live reload. `TestConfigWithIdentitiesIsStatic` loads inline identities, verifies static mode and `IsStatic`, then ensures metadata events do not import dynamic filer identities. `TestReloadStaticConfigMarksNewIdentitiesWithoutFreezingDynamic` checks reloads add new static names without freezing already dynamic identities.

State and persistence behavior: Uses memory credential storage plus temporary JSON files. The core state under test is `useStaticConfig`, `staticIdentityNames`, `Identity.IsStatic`, and the dynamic credential-manager contents.

Dependencies and integration points: Depends on the memory credential store, filer IAM directory constants, metadata entries, and the `newTestS3ApiServerWithMemoryIAM` helper from `auth_credentials_subscribe_test.go`.

Risks and test signals: Prevents operator-created IAM users from being ignored when `-iam.config` contains only advanced STS/OIDC settings. Also protects the established static-file behavior where inline identities are immutable and should not be overwritten by filer reloads.
