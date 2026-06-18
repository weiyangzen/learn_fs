# Research: subset-b-000446

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kms.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kms.go

## Purpose
`kms.go` is the generic KMS dispatch layer for encrypted Ceph OSD keys. It normalizes the configured provider, validates KMS connection details, and routes put/get/update/delete operations to Kubernetes Secrets, Vault, IBM Key Protect, KMIP, or Azure Key Vault. It is the common API used by OSD encryption workflows so the rest of the OSD code can work through one `Config` object rather than directly binding to each backend.

## Important APIs, Types, and Functions
The central type is `Config`, which stores the selected `Provider`, the cluster daemon context, the `CephCluster` spec, and `ClusterInfo`. `NewConfig()` chooses the provider from `clusterSpec.Security.KeyManagementService.ConnectionDetails[KMS_PROVIDER]`, defaulting to Kubernetes when the provider is empty and logging unsupported values. `PutSecret()`, `GetSecret()`, `UpdateSecret()`, and `DeleteSecret()` are the public backend operations. `ValidateConnectionDetails()` enforces mandatory provider fields and loads token-secret data into connection details or process environment. `SetTokenToEnvVar()` is a narrower helper for Vault token injection. `GetParam()` trims whitespace and treats missing or empty entries uniformly. The private `putSecret()`, `getSecret()`, and `deleteSecret()` helpers adapt `libopenstorage/secrets.Secrets`.

## Control Flow
Provider selection is mostly branch based. Kubernetes stores the raw secret in Kubernetes Secret helpers from sibling files. Vault and Azure initialize a `secrets.Secrets` implementation, transform OSD key names with `GenerateOSDEncryptionSecretName()`, and operate with provider-specific key context. IBM creates imported keys with aliases and treats `KEY_ALIAS_NOT_UNIQUE_ERR` as idempotent success. KMIP registers the key with the KMIP server but persists the returned unique identifier in a Kubernetes Secret; later reads and deletes use that identifier to access KMIP. Validation first checks `KMS_PROVIDER`, then token-auth requirements, then provider-specific mandatory fields. Vault `kv` backends get an auto-detected backend version when `VAULT_BACKEND` is absent.

## State and Persistence
State persists in the configured external KMS and, for Kubernetes and KMIP, in Kubernetes Secrets. Vault and Azure secret names are transformed into Rook OSD encryption secret names; KMIP stores only the KMIP unique identifier in Kubernetes, not the encryption key. Vault namespace and KV-v2 destroy behavior are encoded in the key-context map. `ValidateConnectionDetails()` mutates `kms.ConnectionDetails` for IBM/KMIP token content and sets `VAULT_TOKEN` in the process environment for Vault token auth.

## Dependencies and Integration Points
The file integrates with `libopenstorage/secrets`, HashiCorp Vault API constants, IBM Key Protect client types, Kubernetes API errors, Rook `ClusterSpec`, and OSD encryption naming helpers. It calls provider initializers from sibling KMS files: Vault, IBM, KMIP, Azure, and Kubernetes helpers. It is used by OSD prepare/activation and key-rotation paths that need a uniform encrypted-key lifecycle.

## Risks
Provider operations are not an exclusive `switch` in several methods; they rely on mutually exclusive `Is*` checks. Unsupported provider values are logged in `NewConfig()` but leave `Provider` empty, so later operations may silently no-op or return generic unsupported errors depending on method. `getSecret()` assumes `s[secretName]` is a string and can panic if the secrets backend returns an unexpected shape. Vault token validation writes to global process environment, which can leak across tests or concurrent code. IBM delete uses `context.TODO()` because cluster deletion cancels the cluster context; this is intentional but can outlive caller cancellation.

## Test Signals
`kms_test.go` exercises validation for missing provider, Vault token and TLS secrets, IBM token/instance fields, KMIP token material, Azure mandatory fields, and Vault token env injection. It does not deeply mock `PutSecret()`/`GetSecret()`/`DeleteSecret()` backend calls for every provider, so regressions in provider client behavior or `getSecret()` type assertions require integration or provider-specific tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kms.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kms_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kms_test.go

## Purpose
`kms_test.go` validates the generic KMS configuration gate in `kms.go`. It uses fake Kubernetes clients and mutable `KeyManagementServiceSpec` objects to prove that provider-specific mandatory fields, token secrets, TLS secrets, and environment injection behave as expected before any OSD encryption workflow attempts to talk to a KMS.

## Important APIs, Types, and Functions
The main test is `TestValidateConnectionDetails()`, organized as sequential subtests over one fake namespace. It creates token/TLS `Secret` objects for Vault, IBM Key Protect, and KMIP and then calls `ValidateConnectionDetails()`. `TestSetTokenToEnvVar()` calls `SetTokenToEnvVar()` for Vault and asserts `VAULT_TOKEN` is populated from a Kubernetes Secret key named `token`.

## Control Flow
The validation test starts with an empty `ConnectionDetails` map and verifies the missing `KMS_PROVIDER` error. It then mutates shared specs across subtests: KMIP fails before CA and endpoint are present, succeeds after secret data and endpoint are added, Vault fails for absent token Secret, empty token data, missing `VAULT_ADDR`, and missing/empty TLS Secret data, then succeeds once the TLS Secret contains `cert`. IBM fails without token auth, then fails with missing service API key, then missing instance ID, and finally succeeds after both fields are available. Azure validation walks through missing vault URL, tenant ID, client ID, certificate secret name, and success.

## State and Persistence
All persistent state is fake Kubernetes state in the test client. The tests intentionally mutate `kms.ConnectionDetails`, token Secret `Data`, and provider specs over time, so later subtests depend on earlier setup. `TestSetTokenToEnvVar()` mutates process environment and explicitly unsets `VAULT_TOKEN` afterward.

## Dependencies and Integration Points
The test depends on Rook's Kubernetes fake client helper, `cephv1.KeyManagementServiceSpec`, corev1 Secret types, `libopenstorage/secrets` provider constants, and Azure key names. It indirectly covers Vault validation in `vault.go` and mandatory detail constants from IBM, KMIP, and Azure KMS implementations.

## Risks
The subtests are order-dependent because they reuse and mutate the same spec and fake client state. Running subtests in parallel would be unsafe. Assertions focus on exact error strings, which is good for user-facing diagnostics but brittle during error wrapping changes. The test does not cover unsupported provider behavior after `NewConfig()`, backend put/get/delete dispatch, or concurrency effects from process-wide environment variables.

## Test Signals
The strongest signals are exact failures for missing token keys, TLS key names, provider fields, and Azure mandatory fields. The environment test confirms Vault token propagation. Useful additional signals would mock `secrets.Secrets` backends for idempotent `putSecret()` and unsupported-provider paths.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kms_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/vault.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/vault.go

## Purpose
`vault.go` contains Rook's Vault-specific KMS bootstrap and validation logic. It converts CephCluster Vault connection details into the shape expected by `libopenstorage/secrets/vault`, handles TLS material stored in Kubernetes Secrets, validates user configuration, and builds Vault namespace key context for secret operations.

## Important APIs, Types, and Functions
The key public functions are `InitVault()`, `buildVaultKeyContext()`, and `validateVaultConnectionDetails()`. `InitVault()` copies the input config, calls `configTLS()`, converts the resulting map to `map[string]interface{}`, and returns a `secrets.Secrets` Vault implementation. `configTLS()` rewrites TLS connection values from Kubernetes Secret names to temporary certificate/key file paths. `getRemoveCertFilesFunc()` returns cleanup logic for those files. `tlsSecretKeyToCheck()` maps Vault TLS env names to expected Kubernetes Secret keys. `Config.IsVault()` identifies the provider.

## Control Flow
`configTLS()` loops over `cephv1.VaultTLSConnectionDetails`. If a configured TLS value is already under `/etc/vault`, it is treated as a mounted path and left unchanged. Otherwise it fetches the named Kubernetes Secret, creates a temporary file, writes the configured key's bytes with mode `0400`, replaces the config value with the file name, and tracks the file for deferred cleanup. A deferred closure always constructs a cleanup function; on error it immediately removes already-created files and returns nil cleanup to callers. `InitVault()` defers the cleanup after constructing the Vault secret store.

## State and Persistence
TLS files are temporary filesystem state. They exist only long enough for the Vault library to read them, then are closed and removed. The input config is copied before modification so repeated initialization does not permanently replace Secret names with temp paths. Vault namespace state is passed as `secrets.KeyVaultNamespace` in key context only when `VAULT_NAMESPACE` is configured.

## Dependencies and Integration Points
This file integrates with Kubernetes Secrets, Vault API env constants, `libopenstorage/secrets/vault`, and the generic `kms.go` dispatcher. It also supplies validation used by `ValidateConnectionDetails()`, and file paths/constants used by `volumes.go` when mounting Vault secrets into pods.

## Risks
TLS validation checks only existence and non-empty secret data, not certificate validity or key pairing. `configTLS()` uses temporary files outside the pod-mounted `/etc/vault` path when running daemon-side code, so host/container filesystem permissions and cleanup are important. Secret key mapping is asymmetric: `VAULT_CACERT` and `VAULT_CLIENT_CERT` both expect `cert`, while `VAULT_CLIENT_KEY` expects `key`. Any change to Vault TLS connection detail lists must keep this mapping aligned with volume projection logic.

## Test Signals
`vault_test.go` covers TLS key mapping, no-TLS config, already-mounted `/etc/vault` paths, missing Secret errors, successful CA/client cert/client key temp-file generation and cleanup, cleanup on temp file creation failure, and namespace key-context behavior. There is no live Vault integration here; actual auth and secret-store construction depend on provider integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/vault.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/vault_api.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/vault_api.go

## Purpose
`vault_api.go` provides a lower-level Vault API client path used to detect the KV backend version when the user configures Vault KV without explicitly providing `VAULT_BACKEND`. It complements `vault.go`, which initializes the generic libopenstorage Vault secrets implementation.

## Important APIs, Types, and Functions
`newVaultClient()` builds a HashiCorp `api.Client` from Rook KMS connection details. `BackendVersion()` returns `"v1"` or `"v2"` based on explicit config or Vault mount metadata. `trimSlash()` normalizes mount paths for comparison. The package-level `vaultClient` variable points to `newVaultClient` so tests can replace it.

## Control Flow
`newVaultClient()` starts from `api.DefaultConfig()`, copies the secret config to avoid mutation, applies `configTLS()` so TLS values become readable file paths, configures TLS through the libopenstorage Vault utility, creates the API client, sets the trimmed Vault address, optionally sets Vault Enterprise namespace, authenticates via token or Kubernetes auth, and sets the returned token on the client. Authentication errors are wrapped with a more specific Kubernetes-auth message when `VAULT_AUTH_METHOD` is Kubernetes. `BackendVersion()` first honors explicit backend values `kv`, `kv-v2`, `v1`, or `v2`. Otherwise it initializes a client, calls `Sys().ListMounts()`, finds the configured or default backend path, and maps mount option `version=2` to v2, defaulting matched mounts to v1.

## State and Persistence
This file does not persist secrets. It temporarily creates TLS files via `configTLS()` and removes them before returning from client initialization. It reads Vault system mount metadata and authentication state. It mutates only the local copied config and the created client's address, namespace, and token.

## Dependencies and Integration Points
Dependencies include HashiCorp Vault API, `libopenstorage/secrets/vault/utils`, the generic `GetParam()` helper, Vault backend constants, and the TLS configuration path in `vault.go`. `kms.go` calls `BackendVersion()` during validation for Vault KV engines when backend version is omitted.

## Risks
Backend auto-detection requires live Vault connectivity and list-mount permissions during Rook validation. Lack of permissions or unreachable Vault will reject the cluster KMS config even if normal secret operations might later work with explicit version. The package-level `vaultClient` mock hook is convenient but global. Address trimming removes only trailing newline suffixes through `strings.TrimSuffix(..., "\n")`; other whitespace is handled earlier only if values pass through `GetParam()`.

## Test Signals
No dedicated `vault_api_test.go` is in this work item. Coverage is indirect through `kms_test.go` for the path that may call `BackendVersion()` and through `vault_test.go` for TLS file conversion. Stronger signals would mock `vaultClient.Sys().ListMounts()` for explicit v1/v2, missing mount, namespace, and auth-error cases.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/vault_api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/vault_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/vault_test.go

## Purpose
`vault_test.go` verifies the Vault-specific TLS and namespace helpers. Its focus is not live Vault behavior; it locks down how Rook maps Vault TLS env options to Kubernetes Secret keys, rewrites Secret names into temporary files, cleans those files, and builds Vault namespace key context.

## Important APIs, Types, and Functions
`Test_tlsSecretKeyToCheck()` covers the mapping from Vault TLS option names to Kubernetes Secret keys. `Test_configTLS()` is the largest test and drives `configTLS()` through no-op, mounted-path, missing-secret, successful temp-file, advanced CA/client cert/client key, and temp-file failure scenarios. `Test_buildVaultKeyContext()` checks whether `VAULT_NAMESPACE` produces a one-entry key context.

## Control Flow
The TLS test sets debug logging, creates a fake Kubernetes client, and repeatedly calls `configTLS()` with different maps. For Kubernetes-secret TLS values, it creates Secret objects containing `cert` or `key` data and asserts resulting config values differ from the original Secret names and point to existing files. It then calls the returned cleanup function and checks those files are gone. The failure subtest replaces package-level `createTmpFile` and `getRemoveCertFiles` to simulate a temp-file creation failure and verify cleanup runs before returning.

## State and Persistence
The test uses fake Kubernetes Secret state and temporary files on disk. It mutates global package variables `createTmpFile` and `getRemoveCertFiles` in the failure scenario, and sets debug-related environment/log state. The cleanup assertions are important because real Vault initialization briefly writes sensitive TLS material to temp files.

## Dependencies and Integration Points
The test depends on Rook's fake Kubernetes client helper, corev1 Secrets, package-level test hooks from `vault.go`, HashiCorp Vault env option strings, and testify assertions. It also implicitly aligns with `volumes.go`, because both must agree that CA/client cert data is keyed by `cert` and client key data is keyed by `key`.

## Risks
The test's global hook replacement is not reset in a defer in the shown code path, so adding later subtests could inherit mocked functions if not careful. Secret objects are reused through one fake client namespace, making some subtests dependent on earlier created Secrets. It does not exercise malformed file writes except temp creation failure, nor does it validate actual certificate content.

## Test Signals
Strong signals include file existence after TLS conversion and no-file-exists after cleanup, preserving already-mounted `/etc/vault` paths, and returning nil cleanup on errors. Additional useful tests would reset global hooks explicitly and cover `os.WriteFile` failures.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/vault_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/volumes.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/volumes.go

## Purpose
`volumes.go` builds Kubernetes projected volumes and volume mounts for KMS-related secret material needed by OSD prepare/daemon pods. It maps Vault TLS/token Secrets into `/etc/vault` and KMIP certificate/key material into the KMIP config directory.

## Important APIs, Types, and Functions
`VaultSecretVolumeAndMount()` returns the list of `VolumeProjection` entries for Vault TLS and token Secrets. `VaultVolumeAndMount()` and `VaultVolumeAndMountWithCustomName()` wrap those projections in a named `Volume` and `VolumeMount`. `tlsSecretPath()` maps Vault TLS env options to filenames (`vault.ca`, `vault.crt`, `vault.key`). `KMIPVolumeAndMount()` creates a projected volume containing `ca.crt`, `client.crt`, and `client.key`.

## Control Flow
Vault projection generation iterates over `cephv1.VaultTLSConnectionDetails`, checks each configured value with `GetParam()`, and adds a Secret projection with mode `0444`, the expected Secret key from `tlsSecretKeyToCheck()`, and a fixed path from `tlsSecretPath()`. If a token Secret name is provided, it appends a projection of key `token` to `vault.token`. The custom-name variant skips volume creation only when both config map and token name are empty; otherwise it names the volume `vault` plus suffix and mounts it at `/etc/vault` or `/etc/vault/<custom>`.

## State and Persistence
The functions only construct Kubernetes pod specs; persistence is in Kubernetes Secrets mounted as projected volumes. Secret file mode is intentionally world-readable (`0444`) because containers run as the `rook` user while Secrets are mounted as root. The mounts are read-only.

## Dependencies and Integration Points
The file depends on Kubernetes corev1 API types, Vault API option names, `libopenstorage/secrets` provider constants, KMIP constants from sibling files, and `vault.go` key mapping. Operator code can use these helpers when assembling deployments/jobs that need Vault or KMIP credentials.

## Risks
The `len(kmsVaultConfigFiles) == 0` check means a non-empty map with no KMS-related entries still creates an empty projected Vault volume; this is intentionally covered by tests but can surprise callers. `KMIPVolumeAndMount()` assumes the token Secret contains all three required keys and does not support optional entries. Mode `0444` trades stricter permissions for non-root readability.

## Test Signals
`volumes_test.go` covers TLS path mapping, Vault projection combinations for CA/client cert/client key/token, custom volume names and mount paths, empty/non-KMS maps, and KMIP volume projection shape. These tests are structural and do not validate pod admission or Secret existence.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/volumes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/volumes_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/volumes_test.go

## Purpose
`volumes_test.go` verifies that the KMS volume helpers emit exact Kubernetes `VolumeProjection`, `Volume`, and `VolumeMount` structures. It is a spec-shape test suite for Vault and KMIP credential mounts.

## Important APIs, Types, and Functions
`Test_tlsSecretPath()` covers Vault TLS option to mounted filename mapping. `TestVaultSecretVolumeAndMount()` checks projection lists for empty input, CA only, CA plus client cert, CA plus client cert/key, token only, and mixed token/TLS cases. `TestVaultVolumeAndMountWithCustomName()` checks full volume/mount outputs with and without custom suffixes. `TestKMIPVolumeAndMount()` checks KMIP projected Secret items and mount path.

## Control Flow
The tests build expected Kubernetes API objects with mode `0444` and compare returned objects with `reflect.DeepEqual`. Vault projections are expected in the same order as `cephv1.VaultTLSConnectionDetails`, followed by the token projection. Custom Vault names append the suffix to both volume name and `/etc/vault/<suffix>` mount path.

## State and Persistence
There is no external state. The tests construct in-memory Kubernetes API objects only. They encode the persistence contract indirectly: credential data must be supplied by Kubernetes Secrets with keys `cert`, `key`, or `token`, and pods will see files named `vault.ca`, `vault.crt`, `vault.key`, or `vault.token`.

## Dependencies and Integration Points
The suite depends on corev1 Kubernetes types, `libopenstorage/secrets.TypeVault`, Vault env option strings through literals, and KMIP constants. It cross-checks assumptions shared with `vault.go` validation and TLS temp-file conversion.

## Risks
Exact deep equality makes the suite sensitive to harmless Kubernetes struct defaulting differences if helpers start setting optional fields. The tests do not verify invalid/missing Secret names because these helpers are pure pod-spec builders; validation is handled elsewhere. They also do not exercise pod security context interactions with `0444` file mode.

## Test Signals
Good signals are the exhaustive Vault projection combinations and custom mount path checks. Additional signals would include a case for all three KMIP keys with an empty token Secret name if callers might pass empty names.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/kms/volumes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/nsenter.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/nsenter.go

## Purpose
`nsenter.go` provides a small helper for checking or invoking host binaries from inside the Rook container by entering the host mount namespace. It is used by OSD preparation code to ensure host-level tooling such as LVM exists where needed.

## Important APIs, Types, and Functions
`NSEnter` stores a daemon context, target binary name, and binary arguments. `NewNsenter()` constructs it. `buildNsEnterCLI()` produces arguments for `nsenter --mount=/rootfs/proc/1/ns/mnt -- <binary-path> ...`. `callNsEnter()` executes `nsenter` via the configured executor. `checkIfBinaryExistsOnHost()` iterates known host binary directories and succeeds if either executing through `nsenter` works or the binary can be found under `/rootfs`.

## Control Flow
For each candidate directory in `binPathsToCheck`, `checkIfBinaryExistsOnHost()` joins the path with the requested binary and tries to run it in the host mount namespace. If execution fails, it falls back to `os.Stat("/rootfs/<candidate>")` without executing the host binary, avoiding library mismatch problems between container and host. The first successful execution or stat returns nil; exhausting all paths returns an error.

## State and Persistence
The helper has no persistent state. It reads `/rootfs` and invokes the `nsenter` binary. Success depends on container privileges, host mount namespace visibility, and bind-mounted host root.

## Dependencies and Integration Points
It depends on Rook's executor abstraction and is called by `lvmPreReq()` in `volume.go` before LVM mode initialization. It integrates with host paths common to Linux distributions, including NixOS-style `/run/current-system/sw` paths.

## Risks
The fallback `os.Stat()` only proves the binary path exists, not that it can execute successfully in the host namespace. The list of binary directories is hard-coded and may miss unusual distributions. `callNsEnter()` wraps combined output on error, but the outer checker logs failures only at debug level until all candidates fail.

## Test Signals
`nsenter_test.go` verifies CLI construction and a mocked successful lookup for `/usr/sbin/lvm` or `/sbin/lvm`. It does not cover the `/rootfs` stat fallback, all-paths-fail errors, or non-LVM binaries.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/nsenter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/nsenter_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/nsenter_test.go

## Purpose
`nsenter_test.go` locks down the host-binary lookup helper's command shape and happy-path behavior. It ensures OSD preparation will call `nsenter` with the expected mount namespace and target binary arguments.

## Important APIs, Types, and Functions
`TestBuildNsEnterCLI()` creates an `NSEnter` for the LVM check binary and asserts the exact argument slice. `TestCheckIfBinaryExistsOnHost()` uses `exectest.MockExecutor` to simulate successful `nsenter` execution when the candidate binary path is `/usr/sbin/lvm` or `/sbin/lvm`.

## Control Flow
The mocked executor inspects the command and argument positions, returning success only for `nsenter --mount=/rootfs/proc/1/ns/mnt -- /usr/sbin/lvm help` or `/sbin/lvm help`. `checkIfBinaryExistsOnHost()` should stop at the first successful candidate and return nil.

## State and Persistence
The tests are in-memory and do not touch real `/rootfs` or run real `nsenter`. They only assert executor calls.

## Dependencies and Integration Points
The suite depends on the executor test mock, Rook `clusterd.Context`, and the package-level LVM command constant used by `volume.go` prerequisites. It indirectly protects `lvmPreReq()` from command argument drift.

## Risks
Coverage is narrow. There is no test for failed `nsenter` plus successful `/rootfs` stat fallback, no error case when all paths fail, and no path ordering assertion beyond the happy path. The mock also assumes argument positions and may need update if `buildNsEnterCLI()` gains options.

## Test Signals
The existing signals are exact CLI assembly and a successful binary discovery path. Additional signals should include all-candidates-fail and fallback stat behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/nsenter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/remove.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/remove.go

## Purpose
`remove.go` implements OSD removal and replacement cleanup workflows. It validates that requested OSDs are down, marks them out, waits until safe to destroy unless forced, deletes Kubernetes deployments/jobs/PVCs, purges Ceph OSD metadata, optionally removes CRUSH host entries, archives crash warnings, and supports explicit destroy-and-zap replacement cleanup.

## Important APIs, Types, and Functions
`RemoveOSDs()` is the entry point for purging a list of string OSD IDs. `removeOSD()` performs the step-by-step purge. `removeOSDPrepareJob()` deletes prepare Jobs associated with a PVC-backed OSD. `removePVCs()` deletes or detaches data/db/wal PVCs for one OSD set index. `archiveCrash()` archives Ceph crash entries for the OSD. `DestroyOSD()` destroys a specific OSD and zaps its backing device for replacement flows.

## Control Flow
`RemoveOSDs()` writes Ceph config, fetches OSD dump, parses IDs, skips invalid IDs, skips OSDs still marked up, and calls `removeOSD()` for down OSDs. `removeOSD()` gets the CRUSH host, runs `ceph osd out`, loops on `OsdSafeToDestroy()` with sleeps unless `forceOSDRemoval` allows exit, deletes the OSD deployment, derives the PVC name from deployment labels, removes prepare jobs and PVCs, runs `ceph osd purge`, attempts `ceph osd crush rm <host>`, archives crashes, and logs completion. `DestroyOSD()` fetches OSDInfo, runs `ceph osd destroy`, handles PVC-backed encrypted dm removal and mounted device resolution, then runs `ceph-volume lvm zap --destroy`.

## State and Persistence
This file mutates Ceph cluster maps, Kubernetes Deployments, Jobs, PVCs, CRUSH map entries, crash archive state, dmcrypt devices, and block device metadata. With `preservePVC`, PVCs are detached from Rook by removing the OSD PVC ID label rather than deleted. `DestroyOSD()` reads `ROOK_PVC_NAME` for PVC-backed OSD replacement.

## Dependencies and Integration Points
It depends on Ceph client helpers, Kubernetes clientsets, operator OSD label constants, and `Zap`/encryption helpers from OSD code. It bridges operator-level resources with daemon-side Ceph commands and is sensitive to deployment labels created by the OSD operator.

## Risks
`removeOSD()` logs many errors and continues, so partial cleanup is possible. The safe-to-destroy loop can run indefinitely without force. In `removePVCs()`, the code takes labels from `dataPVC` and deletes the OSD PVC ID label from that shared map inside a loop, then applies it to each PVC; this relies on label shape consistency. `archiveCrash()` appears to log "no ceph crash to silence" when `crash != nil`, then iterates `crash`, which suggests a nil-check logic risk. Force removal bypasses safety and can cause data loss by design.

## Test Signals
`remove_test.go` covers PVC deletion for data-only and data/metadata/wal device sets. It does not cover Ceph command sequences, safe-to-destroy looping, deployment deletion, prepare job deletion, preservePVC label detachment, crash archiving, or `DestroyOSD()`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/remove_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/remove_test.go

## Purpose
`remove_test.go` verifies that PVC cleanup for PVC-backed OSD removal selects all PVCs belonging to the same device set and set index, while leaving other OSD PVCs in the set untouched.

## Important APIs, Types, and Functions
`TestRemovePVCs()` drives the private `removePVCs()` helper. `createTestPVCs()` creates test PVCs by instantiating the operator OSD cluster object and calling `PrepareStorageClassDeviceSets()`. `testVolumeClaim()` constructs minimal `VolumeClaimTemplate` values.

## Control Flow
The test installs a fake Kubernetes reactor that fills `GenerateName` PVC names deterministically. The first subtest creates a two-count device set with only a data PVC template, verifies two PVCs exist, calls `removePVCs()` for the first OSD's data PVC, and asserts only the second OSD's PVC remains. The second subtest creates data, metadata, and wal templates for two OSDs, verifies six PVCs, calls `removePVCs()` for one data PVC, and asserts all three PVCs for set index `0` are deleted while the other three remain.

## State and Persistence
State is entirely fake Kubernetes PVC state. The generated names and labels are created through real operator preparation logic, so the test validates compatibility between operator PVC labeling and daemon cleanup selection.

## Dependencies and Integration Points
The test integrates daemon removal code with operator OSD PVC creation code, fake Kubernetes client reactors, storage class device set specs, and OSD label constants. This is useful because `removePVCs()` depends on labels set by a different package.

## Risks
Only the delete path is tested. The `preservePVC=true` path that detaches labels is not covered. The test does not validate prepare Job deletion or deployment-label discovery, so full `removeOSD()` resource cleanup can regress independently. The reactor mutates create actions in place, which is deliberate but tightly coupled to fake client behavior.

## Test Signals
Good signals are set-index isolation and multi-template PVC deletion. Additional coverage should assert preserve mode removes `CephDeviceSetPVCIDLabelKey` without deleting PVCs, and that missing labels or missing data PVCs fail gracefully.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/volume.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/volume.go

## Purpose
`volume.go` is the main daemon-side ceph-volume integration for preparing, listing, and cleaning Ceph OSD block devices. It decides between raw and LVM modes, builds ceph-volume commands for PVC-backed and host devices, parses ceph-volume JSON output into operator `OSDInfo`, updates LVM configuration, wipes stale devices from other clusters, and handles encrypted block device discovery and cleanup.

## Important APIs, Types, and Functions
Data structs `osdInfoBlock`, `osdInfo`, `osdTags`, and `cephVolReportV2` model ceph-volume raw/lvm list and report JSON. `OsdAgent.configureCVDevices()` orchestrates prepare/list behavior. `initializeBlockPVC()`, `initializeDevices()`, `initializeDevicesRawMode()`, and `initializeDevicesLVMMode()` perform command construction for PVC/raw/LVM paths. `allowRawMode()`, `isSafeToUseRawMode()`, and `lvmModeAllowed()` choose mode eligibility. `GetCephVolumeLVMOSDs()` and `GetCephVolumeRawOSDs()` parse existing OSDs. `ZapDevice()`, `WipeDevicesFromOtherClusters()`, `wipeEncryptedDevicesFromOtherClusters()`, and `GetBackingDeviceForEncryptedBlock()` clean stale devices. Smaller helpers cover device class matching, encrypted mapper extraction, ceph-volume logging, database sizing, and OSDInfo dedupe.

## Control Flow
`configureCVDevices()` first handles idempotent no-new-device cases by listing existing LVM then raw OSDs. For new devices it creates an OSD bootstrap keyring, detects LV-backed PVCs, runs PVC raw prepare or non-PVC mode initialization, then lists LVM and raw OSDs again to return authoritative `OSDInfo`. Non-PVC initialization splits eligible devices into raw and LVM maps. Raw mode is denied for encryption, multiple OSDs per device, metadata devices, logical volumes, and unsafe per-device settings. LVM mode builds `ceph-volume lvm batch --prepare` or `lvm prepare` commands, validates report JSON for metadata devices, supports multipath and LV device paths, applies device classes, database sizes, and encrypted flags. Raw listing handles closed encrypted PVC devices by reopening them when passphrase and PVC env vars are available, then closes encrypted devices after preparing.

## State and Persistence
The file mutates host block devices, LVM config, ceph-volume logs, LUKS labels/subsystems, dmcrypt mappings, and OSD metadata. It reads global environment-derived flags `isEncrypted` and `isOnPVC`, plus several OSD env vars during runtime. `UpdateLVMConfig()` rewrites `/etc/lvm/lvm.conf` to disable udev sync/rules and adjust filters. `ZapDevice()` performs destructive cleanup with ceph-volume zap, unmount, wipefs, ceph-bluestore-tool, and `dd` zeroing. `WipeDevicesFromOtherClusters()` clears stale filesystem state on in-memory `LocalDisk` entries after zapping.

## Dependencies and Integration Points
This file is central to OSD agent operation and depends on Rook `clusterd` device discovery, Ceph client bootstrap keyring helpers, operator OSD types/config, encryption helpers from sibling OSD files, executor abstraction, `sys` device parsing, and external binaries (`ceph-volume`, `lvm`, `nsenter`, `cryptsetup`, `wipefs`, `ceph-bluestore-tool`, `dd`, `lsblk`, `sgdisk`, `udevadm`). It returns `oposd.OSDInfo` consumed by operator activation and deployment logic.

## Risks
The code is intentionally command-heavy and environment-sensitive. Package globals such as `isEncrypted` and `isOnPVC` are initialized at package load, so tests or callers that mutate env vars later may not affect those booleans. Several paths are destructive (`ZapDevice`, stale cluster wipe) and depend on correct matching of desired devices, DevLinks, and cluster FSIDs. Ceph-volume report validation is critical for metadata devices; missing or malformed JSON can block preparation. LVM config rewriting uses byte replacements and assumes expected default text is present. Raw/LVM listing behavior differs for PVC versus host devices, with stricter errors on PVC when a foreign cluster OSD is found.

## Test Signals
`volume_test.go` is broad: it covers PVC raw and LVM idempotency, raw mode on partitions/disks, LVM argument construction for encryption, multiple OSDs, metadata devices, partitions, LVs, by-id/by-path links, multipath devices, encrypted mapper parsing, ceph-volume raw/lvm JSON parsing, multi-cluster filtering, raw-mode eligibility, OSDInfo dedupe, stale device wiping, and device class matching. It still relies heavily on mocked command argument positions rather than live ceph-volume behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/volume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/volume_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/osd/volume_test.go

## Purpose
`volume_test.go` is the main behavioral safety net for daemon-side ceph-volume orchestration. It mocks external command execution to verify the OSD agent builds correct raw/LVM commands, parses ceph-volume output, handles PVC-backed devices, respects device classes, and zaps stale devices from other clusters.

## Important APIs, Types, and Functions
The suite defines representative ceph-volume JSON fixtures for LVM, raw, encrypted raw, partitions, multi-cluster reports, and LVM symlink paths. Major tests include `TestConfigureCVDevices()`, `TestInitializeBlock()`, `TestInitializeBlockPVC()`, `TestInitializeBlockPVCWithMetadata()`, `TestParseCephVolumeLVMResult()`, `TestParseCephVolumeRawResult()`, `TestCephVolumeResultMultiClusterSingleOSD()`, `TestCephVolumeResultMultiClusterMultiOSD()`, `TestAllowRawMode()`, `TestAppendOSDInfo()`, `TestIsSafeToUseRawMode()`, `TestLVMModeAllowed()`, `TestWipeDevicesFromOtherClusters()`, `TestFindDeviceClass()`, and `TestGetCephVolumeRawOSDsHonorDeviceClass()`.

## Control Flow
Mock executors inspect command names and positional arguments to emulate `ceph-volume`, `lsblk`, `sgdisk`, `cryptsetup`, `wipefs`, `ceph-bluestore-tool`, and `dd`. The tests drive both new-device and no-available-device flows. PVC tests check LV-backed detection and raw/lvm listing behavior. LVM initialization tests assert command variants for default, encrypted, multiple OSDs per device, device class, metadata devices, partitions, existing LVs, multipath, by-id/by-path references, and metadata report validation. Parsing tests assert cluster FSID filtering and OSD count. Wipe tests ensure only desired stale devices are zapped and that encrypted mapper devices resolve to backing devices.

## State and Persistence
The tests use temporary files for `lvmConfPath`, temporary ceph config dirs, environment variables such as OSD store type and device class, and package-level globals like `cvLogDir`. They simulate persistent device state through `clusterd.Context.Devices` and fake ceph-volume JSON rather than touching real disks. Some tests mutate package variables and environment, so isolation discipline matters.

## Dependencies and Integration Points
The suite connects OSD volume code with Rook config types, Ceph version structs, operator OSD `OSDInfo`, store config, executor test mocks, `sys.LocalDisk`, and fake Kubernetes clients for raw OSD device class population. It protects many command contracts that activation, replacement, and cleanup code depend on.

## Risks
The tests are broad but brittle because many assertions depend on exact argument indexes. They do not execute real ceph-volume or validate actual device effects. Environment-derived production globals initialized at package load are hard to vary reliably in tests. Several cases use large in-test fixtures, so maintaining fixture accuracy with new ceph-volume versions is important.

## Test Signals
Strong signals include raw/LVM mode selection, metadata-device command formation, report JSON validation, foreign cluster filtering, destructive zap sequence, DevLinks matching, and per-device class override behavior. Useful additions would include explicit `UpdateLVMConfig()` content assertions and failure-path coverage for malformed raw JSON, failed wipefs, and closed encrypted PVC reopening.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/osd/volume_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/util/util.go -->
# sources/control-plane/rook/pkg/daemon/ceph/util/util.go

## Purpose
`util.go` contains small Ceph daemon utility helpers for parsing endpoint strings into host and port components. It is a shared support file for code that needs to split monitor or daemon endpoint addresses.

## Important APIs, Types, and Functions
`GetIPFromEndpoint(endpoint string) string` returns the host portion from `net.SplitHostPort()`. `GetPortFromEndpoint(endpoint string) int32` returns the parsed port as a 32-bit integer. A package logger records parse failures.

## Control Flow
Both helpers call `net.SplitHostPort(endpoint)`. `GetIPFromEndpoint()` logs an error and returns the zero-value host string when splitting fails. `GetPortFromEndpoint()` logs a split failure, otherwise parses the port string with `strconv.ParseInt(..., 10, 32)`, logs parse failures, and returns the resulting `int32` value, which is zero on failure.

## State and Persistence
There is no persisted state. The only side effect is logging. Failed parsing returns zero values rather than errors.

## Dependencies and Integration Points
The helpers depend on Go's `net` and `strconv` packages and Rook's capnslog logger. Callers must provide endpoints in `host:port` form accepted by `net.SplitHostPort`, including bracketed IPv6 addresses when applicable.

## Risks
Returning zero values on parse failure can hide invalid endpoints if callers do not separately validate input. `GetPortFromEndpoint()` logs a split failure with `portString`, which is empty in that branch. The API cannot distinguish an actual port `0` from an invalid endpoint. No tests are included in this work item.

## Test Signals
Useful tests would cover IPv4 `1.2.3.4:6789`, DNS names, bracketed IPv6, missing port, non-numeric port, and out-of-range port values. Callers should also have validation tests if port zero is not acceptable.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/util/util.go -->
