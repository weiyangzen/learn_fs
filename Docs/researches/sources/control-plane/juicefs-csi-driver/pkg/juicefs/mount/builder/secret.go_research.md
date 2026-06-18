## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/secret.go

### Purpose
`secret.go` builds the Kubernetes Secret used by JuiceFS mount pods, jobs, and sidecars. The Secret carries serialized settings, credentials, env values, optional session tokens, init config, and the `check_mount.sh` script used by sidecar lifecycle hooks.

### Important APIs, Types, And Functions
Constants define `checkMountScriptName`, `checkMountScriptDir`, and `checkMountScriptPath`. `checkMountScriptContent` polls for a JuiceFS mount and optionally sets quota for subpaths. `BaseBuilder.NewSecret()` creates a labeled `corev1.Secret`. `BaseBuilder.GetEnvKey()` returns secret keys that should be exposed as env vars. Owner helpers are `SetPodAsOwner`, `SetPVCAsOwner`, `SetPVAsOwner`, and `SetJobAsOwner`.

### Control Flow
`NewSecret` collects non-empty sensitive settings into `StringData`, always includes `jfsSettings`, adds `check_mount.sh` after replacing placeholder characters with backticks, parses format options to extract `session-token`, then copies arbitrary `jfsSetting.Envs`. It sets namespace/name from the setting and labels the secret as a JuiceFS secret. Owner helpers overwrite owner references with a single owner reference suited to garbage collection.

### State, Persistence, And Dependencies
The output Secret persists credentials and scripts in Kubernetes. It depends on `config.JfsSetting`, Kubernetes core/batch/meta APIs, and `common.JuicefsSecretLabelKey`. Data includes cleartext StringData before Kubernetes stores it, so logging must avoid dumping secrets.

### Integration Points
`PodBuilder` and `JobBuilder` expect secret keys to exist for generated env `SecretKeyRef`s. Sidecar builders mount `check_mount.sh` from this Secret. `PodMount` creates/updates the Secret and sets PV or Job owners; sidecar injection likely sets pod/PVC ownership depending on lifecycle.

### Risks
Arbitrary environment keys can override expected keys if names collide. `GetEnvKey` detects `session-token` with a substring check, while `NewSecret` parses options; mismatches are possible on malformed options. Owner helper calls replace existing references rather than appending. The embedded shell script must remain executable and safe because it runs in container lifecycle hooks.

### Test Signals
`secret_test.go` verifies `GetEnvKey` includes meta URL, secret keys, token, passphrase, and custom env keys. Additional useful tests would check `session-token`, check script presence, label/namespace/name, and owner reference shapes.
