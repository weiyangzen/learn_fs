# sources/control-plane/juicefs-csi-driver/pkg/config/command.go

Purpose: generates JuiceFS `auth` and `format` command arguments and retrieves CE volume UUIDs. It separates real CSI-side args from mount-pod command args where secrets are represented by environment variables.

Important functions: `KeysCompatible` rewrites legacy secret keys to canonical dashed names. `GenAuthCmd` validates `name`, escapes args, strips token/secret/passphrase values in pod args, handles `JFS_NO_UPDATE_CONFIG`, writes `initconfig` when applicable, appends format options, and adds `--conf-dir`. `GenFormatCmd` validates `name` and `metaurl`, handles `--no-update`, storage keys, stripped `secret-key`, and format options. `GetJfsVolUUID` runs `juicefs config` for CE and parses `"UUID"`, while EE returns `s.Name`.

State and dependencies: `KeysCompatible` mutates the secrets map. `GenAuthCmd` may write a config file. `GetJfsVolUUID` spawns a subprocess with `s.Envs`. Uses package globals, gRPC status errors, k8s exec utilities, and `security.EscapeBashStr`.

Risks: UUID parsing uses regex over CLI output instead of JSON decoding. Legacy key rewriting can overwrite canonical keys. `JFS_NO_UPDATE_CONFIG` changes validation and filesystem behavior. Command generation has limited direct tests.

Test signals: `command_test.go` covers UUID success, subprocess error, and EE shortcut only.
