<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/secret.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/secret.go

### Purpose
`secret.go` validates JuiceFS Secret content before admission, including config path shape, env serialization, and basic connectivity/authentication against CE or EE JuiceFS backends.

### Important APIs, Types, And Functions
`SecretValidator` wraps a `juicefs.Interface`. `NewSecretValidator` constructs it. `Validate(ctx, secret)` validates special `configs` and `envs` keys, builds a string secret map, obtains a `JfsSetting`, creates a temporary client config directory, and calls either `Status` for CE or `AuthFs` for EE. `ValidateConfigs` parses YAML/JSON into path mappings and requires non-empty absolute paths. `ValidateEnvs` parses YAML/JSON env maps.

### Control Flow
`Validate` first validates structured optional fields. It then copies all `secret.Data` bytes into strings, calls provider `Settings`, creates a temp dir under `os.TempDir`, assigns it to `ClientConfPath`, and defers cleanup. CE mode requires non-empty `metaurl` and calls `Status`; EE mode calls `AuthFs` in force mode.

### State, Persistence, And Dependencies
Temporary filesystem state is created and removed. External state may be contacted through the JuiceFS provider status/auth calls. Dependencies include Kubernetes Secrets, project config parsing helpers, the JuiceFS interface, and standard filesystem utilities.

### Integration Points
`SecretHandler` calls this validator for Kubernetes validating admission. Installed webhook configuration selects Secrets labeled for validation, so users can preflight mount secrets before workloads consume them.

### Risks
Validation can be slow or flaky because it can contact external metadata/auth services during admission. `failurePolicy` in manifests is Ignore, so validation failures may not block depending on installation. `ValidateConfigs` requires absolute paths but does not validate path existence. All secret bytes are converted to strings, which is fine for current config fields but unsuitable for arbitrary binary data.

### Test Signals
Needed tests include invalid configs YAML/JSON, empty config values, relative config paths, valid env maps, invalid env serialization, missing CE metaurl, provider `Settings` error, CE `Status` error, EE `AuthFs` error, temp-dir creation failure, and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/secret.go -->
