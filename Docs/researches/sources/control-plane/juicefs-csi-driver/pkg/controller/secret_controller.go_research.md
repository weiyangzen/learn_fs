# sources/control-plane/juicefs-csi-driver/pkg/controller/secret_controller.go

## Purpose
`SecretController` watches PV-referenced JuiceFS secrets, cleans legacy orphan mount-pod secrets, and maintains enterprise `initconfig` content inside Kubernetes Secret data.

## Important APIs, Types, And Functions
Key functions are `checkAndCleanOrphanSecret`, `refreshSecretInitConfig`, `SecretController.Reconcile`, `shouldSecretInQueue`, and `SetupWithManager`. Important annotations are `juicefs/last-update-at` and `juicefs/secret-fields-hash`.

## Control Flow
`checkAndCleanOrphanSecret` filters to legacy CSI namespace secrets named `juicefs-*-secret`, skips newly created or labeled secrets, requires JuiceFS token/meta fields and `check_mount.sh`, and deletes the secret if the corresponding mount pod no longer exists. `refreshSecretInitConfig` loads the secret, skips CE/metaurl or incomplete secrets, builds JuiceFS settings, hashes auth-sensitive fields, throttles refreshes when unchanged and recently updated, prepares temporary config files for ceph/gs credential mounts, runs `jfs.AuthFs`, reads the generated client config, and updates Secret `StringData` plus annotations. `Reconcile` fetches the secret, performs orphan cleanup, refreshes init config, and requeues after `config.SecretReconcilerInterval`.

## State And Persistence
Persistent state is the Kubernetes Secret data and annotations, especially `initconfig`, update time, and field hash. Temporary filesystem state is created under `os.TempDir()` and, for ceph/gs config secrets, potentially at backend-specific mount paths, then cleaned by defers. Queue eligibility depends on the in-memory `watchedSecrets` map populated by `PVController`.

## Dependencies And Integration Points
The controller integrates with JuiceFS auth/settings generation, `config.KeysCompatible`, Kubernetes secrets, PV controller state, and controller-runtime secret watches. It also interacts with storage-backend config secrets for ceph and Google storage credentials.

## Risks
This path writes local credential files to configured mount paths and must clean them reliably; existing files are treated as errors to avoid overwrites. Failed forced auth removes stale `initconfig` from local maps before updating the Secret, which can affect mounts that rely on it. The queue depends on PV discovery, so a secret created before its PV is observed is ignored until watched. The update writes `StringData` from all current secret data, so binary or large secret values should be considered carefully.

## Test Signals
No direct tests are in this subset. High-value tests would cover hash/throttle behavior, CE/metaurl skips, auth-failure deletion of `initconfig`, ceph/gs config file cleanup, and orphan secret deletion.
