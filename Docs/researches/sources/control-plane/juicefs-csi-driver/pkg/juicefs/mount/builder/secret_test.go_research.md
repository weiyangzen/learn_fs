## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/secret_test.go

### Purpose
`secret_test.go` tests the env-key projection contract for Secrets. It verifies that `BaseBuilder.GetEnvKey()` returns expected secret keys for configured credentials and custom env values.

### Important APIs, Types, And Functions
The sole test is `TestBaseBuilder_GetEnvKey`. It builds a `BaseBuilder` with a `JfsSetting` containing `MetaUrl`, `SecretKey`, `SecretKey2`, `Token`, `Passphrase`, and `Envs`, then compares the returned slice with the expected key list.

### Control Flow
The table test directly calls `GetEnvKey()` and uses `reflect.DeepEqual`. There is no Kubernetes fake client and no Secret object creation.

### State, Persistence, And Dependencies
The test has no persistent state. It depends on `config.JfsSetting` and Go reflection.

### Integration Points
This is a small guard for the env variables later emitted by common pod/job generation. If `GetEnvKey` omits a key, generated containers may not receive the corresponding credential SecretKeyRef.

### Risks
The test does not cover `session-token`, `SecretKey2` ordering with maps beyond one custom env, `EncryptRsaKey`, `InitConfig`, actual Secret contents, labels, or owner references. Because Go map iteration order is random, multiple `Envs` entries could make strict slice ordering brittle.

### Test Signals
Failure indicates a credential/env key contract change. Broader coverage would assert `NewSecret().StringData` and env key behavior from parsed format options.
