# subset-b-000345 Research

Grouped research for Ceph-CSI health checker, journal, KMS, liveness, and NFS source files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/checker.go -->
# sources/control-plane/ceph-csi/internal/health-checker/checker.go

## Purpose
`checker.go` defines the shared runtime state and lifecycle helpers for health checkers. It does not perform a check itself; concrete checkers embed `checker`, call `initDefaults()`, and provide `runChecker`.

## Important APIs, Types, And Functions
`command` is the private control-channel command type, with `stopCommand` as the only command. `checker` stores interval, timeout, a read/write mutex, `isRunning`, health result, last error, last update time, command channel, and the concrete `runChecker` callback. `initDefaults()`, `start()`, `stop()`, and `isHealthy()` are the common implementation used by `fileChecker` and `statChecker`.

## Control Flow And State
`initDefaults()` sets a 60 second interval, 15 second timeout, healthy initial status, current `lastUpdate`, and a default panic callback. `start()` only launches a goroutine if `isRunning` is false. `stop()` sends a `STOP` command synchronously to the checker goroutine. `isHealthy()` marks a checker unhealthy when no successful update has happened within `interval + timeout`, then returns a consistent `healthy, err` pair under a read lock.

## Dependencies And Integration Points
This file depends only on `fmt`, `sync`, and `time`. It is consumed through the `ConditionChecker` interface in `manager.go`, with concrete behavior supplied by `filechecker.go` and `statchecker.go`.

## Risks And Edge Cases
`isRunning` is read and written without mutex protection, so concurrent `start()`, `stop()`, and tests can race under the Go race detector. `stop()` can block forever if called before the goroutine is ready to receive or after the checker loop has exited. `start()` sets `isRunning` inside the goroutine, so rapid duplicate starts may launch more than one checker.

## Test Signals
Coverage comes indirectly from file/stat checker and manager tests. The tests exercise lifecycle and health reads, but they do not check timeout-induced unhealthy state, duplicate starts, race behavior, or `stop()` blocking paths.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/checker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/filechecker.go -->
# sources/control-plane/ceph-csi/internal/health-checker/filechecker.go

## Purpose
`filechecker.go` implements a health checker that proves a volume path is writable and readable by writing a JSON timestamp file and reading it back.

## Important APIs, Types, And Functions
`fileChecker` embeds `checker` and stores `filename`, always `<dir>/csi-volume-condition.ts`. `newFileChecker(dir)` constructs the checker and installs its loop. `readTimestamp()` reads and JSON-decodes a `time.Time`; `writeTimestamp()` JSON-encodes a timestamp and writes it with mode `0644`.

## Control Flow And State
The checker loop starts a ticker at `interval`. On each tick it writes the tick timestamp, reads the file, compares the value exactly with `now`, and updates `healthy`, `err`, and `lastUpdate` under the mutex. Any write, read, unmarshal, or mismatch error marks the checker unhealthy and keeps the loop running. A command received on `commands` clears `isRunning` and exits.

## State And Persistence Behavior
The persistent side effect is a timestamp file in the volume path. The file is overwritten on every successful tick and can be inspected for debugging. Health state itself is in memory and is lost when the checker object is discarded.

## Dependencies And Integration Points
The implementation uses `os.ReadFile`, `os.WriteFile`, `path.Join`, `time.Time.MarshalJSON`, and `time.Time.UnmarshalJSON`. It is created by `healthCheckManager.startFileChecker()` for `FileCheckerType`.

## Risks And Edge Cases
The first actual I/O check does not happen until the first ticker event, while the default state is healthy. Exact timestamp comparison relies on the same JSON round trip and local filesystem write/read visibility. The file mode permits world-readable timestamp metadata. Parent directory absence, read-only mounts, stalled I/O, or corrupted timestamp contents all surface as unhealthy errors.

## Test Signals
`filechecker_test.go` starts a checker against a temporary directory, waits for it to run, repeatedly checks healthy status, and verifies direct write/read helpers. It does not force write failures, read corruption, timestamp mismatch, or timeout handling.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/filechecker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/filechecker_test.go -->
# sources/control-plane/ceph-csi/internal/health-checker/filechecker_test.go

## Purpose
`filechecker_test.go` validates the basic lifecycle and timestamp helpers for the file-backed health checker.

## Important APIs, Types, And Functions
`TestFileChecker` constructs a checker through `newFileChecker`, type asserts it to `*fileChecker`, shortens the interval, starts it, probes `isRunning`, repeatedly checks `isHealthy()`, and stops it. `TestWriteReadTimestamp` writes and reads a timestamp in a temporary directory.

## Control Flow And Test Behavior
Both tests run in parallel and use `t.TempDir()` to isolate filesystem state. The lifecycle test sleeps one second after start and then polls health ten times at one second intervals, while the checker interval is five seconds.

## Dependencies And Integration Points
The tests use the concrete `fileChecker` type rather than only the `ConditionChecker` interface so they can tune the interval and inspect `isRunning`.

## Risks And Edge Cases
The lifecycle test is timing-sensitive and assumes the goroutine starts within one second. It observes `isRunning` without synchronization. Because initial health is true and the first check happens later, the test can pass before much real I/O has occurred.

## Test Signals
The file confirms normal temporary-directory operation and JSON timestamp round trip. Missing coverage includes failed writes, failed reads, corrupt timestamp files, stale update timeout, duplicate starts, and blocking stop behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/filechecker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/manager.go -->
# sources/control-plane/ceph-csi/internal/health-checker/manager.go

## Purpose
`manager.go` provides the public health-check manager that owns checkers per volume and path. It lets callers start, stop, and query file-based or stat-based checkers, with an option for shared checkers that ignore path at lookup time.

## Important APIs, Types, And Functions
`CheckerType` is a bitmask with `FileCheckerType` and `StatCheckerType`. `Manager` exposes `StartSharedChecker`, `StartChecker`, `StopSharedChecker`, `StopChecker`, and `IsHealthy`. `ConditionChecker` abstracts `start`, `stop`, and `isHealthy`. `healthCheckManager` stores `map[string]ConditionChecker` protected by `sync.Mutex`. `fallbackKey(volumeID, path)` joins volume and path for non-shared checkers.

## Control Flow And State
`NewHealthCheckManager()` initializes an empty checker map. Start methods call `createChecker()`, which dispatches to `startFileChecker()` and/or `startStatChecker()` based on the bitmask. `startChecker()` inserts only when the key is absent and starts the checker immediately. Stop methods look up the key, call `stop()`, and delete the entry. `IsHealthy()` checks the shared volume key first, then falls back to the volume/path key, returning `(true, error)` when no checker exists.

## State And Persistence Behavior
Manager state is purely in memory. Shared checkers use `volumeID` as key; non-shared checkers use `volumeID + path`, so multiple mount paths for the same volume can be tracked independently. Persistent health behavior is delegated to concrete checker implementations.

## Dependencies And Integration Points
The manager integrates concrete constructors from `filechecker.go` and `statchecker.go`. It is the package-level orchestration surface expected by CSI volume health logic.

## Risks And Edge Cases
`StartChecker` with both file and stat bits tries both under the same key; the second start sees the key already present and returns a duplicate error. The map lock does not protect fields inside the checker after start. Returning healthy with an error for missing checkers is unusual and relies on callers reading the error. Synchronous `stop()` may block if the checker goroutine is not consuming commands.

## Test Signals
`manager_test.go` covers missing checker queries, start/stop of a stat checker, shared path-insensitive lookup, and independent non-shared checkers for the same volume. It does not cover file checker creation through the manager, duplicate start errors, combined checker bitmasks, or concurrent start/stop/query behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/manager_test.go -->
# sources/control-plane/ceph-csi/internal/health-checker/manager_test.go

## Purpose
`manager_test.go` verifies basic manager semantics for missing, shared, and non-shared stat checkers.

## Important APIs, Types, And Functions
`TestManager` exercises normal `StartChecker`, `IsHealthy`, and `StopChecker`. `TestSharedChecker` verifies `StartSharedChecker` stores a checker under volume ID only and ignores path during lookup. `TestTwoNonSharedChecker` verifies two different paths for the same volume are independent.

## Control Flow And Test Behavior
Tests use temporary directories and the same fake volume ID. They start `StatCheckerType` checkers only, query health immediately, and stop the checkers at the end. `require.ErrorContains` asserts missing non-shared path lookup reports no checker.

## Dependencies And Integration Points
The tests depend on `testify/require` and package-private manager behavior. They indirectly instantiate stat checkers, so they depend on the host filesystem allowing `os.Stat` on temporary directories.

## Risks And Edge Cases
The assertions contain repeated checks against the earlier `err` variable instead of the newly returned `msg` in some places, which weakens failure detection. No race detector behavior is asserted, and there is no cleanup defer if a fatal assertion happens after a checker has been started.

## Test Signals
The tests document intended keying semantics: shared checkers shadow path-specific lookup, and non-shared checkers are isolated by path. Coverage gaps include file checkers, duplicate keys, invalid checker types, combined type bitmasks, and concurrent usage.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/statchecker.go -->
# sources/control-plane/ceph-csi/internal/health-checker/statchecker.go

## Purpose
`statchecker.go` implements a lightweight health checker that calls `os.Stat` on a volume path to detect disappearance or inaccessible filesystem state.

## Important APIs, Types, And Functions
`statChecker` embeds `checker` and stores the checked directory path. `newStatChecker(dir)` constructs the checker and installs a ticker-driven `runChecker` implementation.

## Control Flow And State
The loop starts a ticker using `interval`, listens for stop commands, and otherwise calls `os.Stat(sc.dir)`. A stat error marks the checker unhealthy and preserves the error. A successful stat marks the checker healthy, clears `err`, and updates `lastUpdate` to the tick time.

## State And Persistence Behavior
There are no persistent writes. The checker only observes filesystem metadata and keeps in-memory health state.

## Dependencies And Integration Points
The implementation depends on `os.Stat` and the shared `checker` behavior. It is selected by `healthCheckManager.startStatChecker()` for `StatCheckerType`.

## Risks And Edge Cases
The first check is delayed until the ticker fires, so a missing path may initially report healthy. `os.Stat` cannot prove read/write health and only validates the path exists and can be stated. Slow or blocked stat calls are handled indirectly by `checker.isHealthy()` timeout detection.

## Test Signals
`statchecker_test.go` validates a temp directory remains healthy through several polling iterations. It does not remove the directory, simulate permission failures, or exercise timeout behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/statchecker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/statchecker_test.go -->
# sources/control-plane/ceph-csi/internal/health-checker/statchecker_test.go

## Purpose
`statchecker_test.go` validates the basic lifecycle of the stat-based health checker.

## Important APIs, Types, And Functions
`TestStatChecker` constructs a checker with `newStatChecker`, type asserts it to `*statChecker`, shortens the interval, starts it, checks `isRunning`, repeatedly calls `isHealthy()`, and stops it.

## Control Flow And Test Behavior
The test uses a temporary directory, sleeps for goroutine startup, and polls health for ten seconds while the checker ticks every five seconds.

## Dependencies And Integration Points
The test depends on the package-private concrete type to tune timing and on host filesystem behavior for `os.Stat`.

## Risks And Edge Cases
The test reads `isRunning` without synchronization and has wall-clock sleeps. It mainly verifies that the happy path does not fail; it does not assert a stat call actually happened before early health reads.

## Test Signals
The test confirms normal stat checking against a live directory. Missing coverage includes missing path after startup, permission errors, stalled `os.Stat`, duplicate starts, and stop blocking.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/health-checker/statchecker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/journal/omap.go -->
# sources/control-plane/ceph-csi/internal/journal/omap.go

## Purpose
`omap.go` centralizes low-level RADOS OMAP operations used by CSI journal code. It fetches, lists, sets, and removes OMAP keys while normalizing common Ceph errors to Ceph-CSI utility errors.

## Important APIs, Types, And Functions
`chunkSize` controls `ListOmapValues` pagination. `getOMapValues()` fetches selected keys by iterating OMAP entries with a prefix. `listOMapValues()` returns all keys under a prefix. `setOMapKeys()` writes key/value pairs. `removeMapKeys()` removes keys and tolerates missing OMAP objects. `omapPoolError()` wraps missing pool errors as `util.ErrPoolNotFound`.

## Control Flow And State
Each operation obtains an IO context from the journal connection, sets the namespace when configured, performs a RADOS OMAP operation, logs results, and destroys the IO context. List operations advance `startAfter` from the last key seen until no new keys are returned or an error occurs.

## State And Persistence Behavior
State lives in Ceph RADOS OMAP objects. Values are stored as strings converted to byte slices. Missing pools and missing OMAP objects are mapped differently depending on operation: fetch/list treat missing objects as `util.ErrKeyNotFound`, while remove treats missing objects as a non-error for backward compatibility.

## Dependencies And Integration Points
The file depends on `github.com/ceph/go-ceph/rados`, `util.ClusterConnection`, and Ceph-CSI logging. `voljournal.go` and `volumegroupjournal.go` build reservation semantics on top of these helpers.

## Risks And Edge Cases
`getOMapValues()` lists through the prefix and filters in memory instead of using direct key retrieval, so large OMAP objects still require pagination. If a key is not in the requested prefix, it will not be found even if listed in `keys`. The missing-object behavior differs between removal and reads, so callers must understand idempotent cleanup semantics.

## Test Signals
No direct tests are included in this subset. Higher-level journal flows should test missing pool, missing OMAP, namespace, prefix filtering, pagination, set/remove idempotency, and logging-safe handling of sensitive values.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/journal/omap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/journal/voljournal.go -->
# sources/control-plane/ceph-csi/internal/journal/voljournal.go

## Purpose
`voljournal.go` implements Ceph-CSI volume and snapshot journal metadata. It preserves idempotency between orchestrator request names and generated Ceph object UUIDs, stores attributes in RADOS OMAPs, supports cleanup of stale reservations, and provides helper mappings for migration and mirroring.

## Important APIs, Types, And Functions
`Config` defines all OMAP object names and keys for volumes or snapshots. Constructors include `NewCSIVolumeJournal`, `NewCSISnapshotJournal`, and namespace-aware variants. `Connection` wraps a `util.ClusterConnection` and journal config. `ImageData` and `ImageAttributes` carry decoded reservation state. Main methods include `Connect`, `CheckReservation`, `UndoReservation`, `ReserveName`, `GetImageAttributes`, `StoreImageID`, `StoreAttribute`, `StoreGroupID`, `FetchAttribute`, `CheckNewUUIDMapping`, `ReserveNewUUIDMapping`, and `ResetVolumeOwner`.

## Control Flow And State
`CheckReservation()` looks up the request-name key in the CSI directory OMAP, decodes either legacy UUID-only or poolID/UUID values, resolves pool IDs to pool names, fetches per-object attributes, validates back-pointers, snapshot source, KMS ID, and encryption type, and cleans stale reservations when key data is missing. `ReserveName()` reserves a UUID OMAP first, writes the request-to-UUID mapping, then writes the per-UUID back-pointer and image metadata, with deferred cleanup on later failure. `UndoReservation()` deletes the UUID OMAP and then removes the request-name key.

## State And Persistence Behavior
Persistent state is split between a global CSI directory OMAP and per-UUID OMAP objects. Directory keys map CO names or old volume handles to UUIDs or encoded poolID/UUID values. Per-UUID OMAPs store request name, image name, image ID, group ID, snapshot source, encryption KMS, encryption type, owner, backing snapshot ID, and arbitrary prefixed attributes. The connection caches monitors, credentials, and the go-ceph cluster connection.

## Dependencies And Integration Points
The file depends on `go-ceph`, Google UUIDs, `util.CSIIdentifier`, pool lookup helpers, Ceph-CSI crypto types, and the OMAP helpers in `omap.go`. RBD, CephFS, NFS, and migration code use these methods to maintain idempotent volume and snapshot metadata.

## Risks And Edge Cases
The code expects callers to hold a request-name lock; without it, parallel create/delete operations can corrupt mappings. Crash windows exist between UUID object reservation, directory mapping, and per-UUID metadata writes, with later cleanup expected to recover. The non-legacy poolID decoding assumes a slash-separated value with expected components. `Destroy()` only clears metadata and does not call `conn.Destroy()`, so caller ownership of the cluster connection is important.

## Test Signals
No tests for this file are in the subset. High-value coverage would include legacy and poolID encoded mappings, stale cleanup paths, snapshot parent mismatch, KMS/encryption mismatch, UUID parse failures in undo, namespace behavior, arbitrary attribute store/fetch, and crash-window reconciliation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/journal/voljournal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/journal/volumegroupjournal.go -->
# sources/control-plane/ceph-csi/internal/journal/volumegroupjournal.go

## Purpose
`volumegroupjournal.go` extends the journal pattern to CSI volume groups and volume group snapshots. It maps request names to generated group UUIDs/names and stores member volume mappings plus creation time in RADOS OMAPs.

## Important APIs, Types, And Functions
`VolumeGroupJournal` is the public interface for group journal operations. `VolumeGroupJournalConfig` embeds `Config` and adds a creation-time key. `volumeGroupJournalConnection` binds config to a `Connection`. Constructors include `NewCSIVolumeGroupJournal` and namespace-aware variants. Key methods are `Connect`, `Destroy`, `CheckReservation`, `UndoReservation`, `ReserveName`, `GetVolumeGroupAttributes`, `AddVolumesMapping`, `RemoveVolumesMapping`, `MakeVolumeGroupID`, and `generateVolumeGroupName`.

## Control Flow And State
`ReserveName()` reserves a UUID OMAP, creates the request-name mapping, writes request name, generated group name, and creation time into the UUID object, and defers cleanup on failure. `CheckReservation()` looks up a request-name mapping, fetches UUID attributes, validates the back-pointer request name, and returns `VolumeGroupData`. `UndoReservation()` removes the per-UUID object and then removes the request-name key. Mapping methods add or remove volume IDs from the group UUID OMAP.

## State And Persistence Behavior
Group state is persisted in RADOS OMAPs named with `csi.groups.<suffix>` and per-group UUID OMAPs. Per-group attributes include request name, group name, creation time, and remaining key/value pairs treated as volume-to-value mappings. `CreationTime` is marshaled as text and optional on read.

## Dependencies And Integration Points
This file reuses `Config`, `Connection`, `reserveOMapName`, OMAP helpers, UUID parsing, `util.CSIIdentifier`, and Ceph-CSI logging. It integrates with group snapshot/volume group workflows that need idempotent request-name reservation.

## Risks And Edge Cases
As with volume reservations, callers must externally serialize by request name. If a crash occurs after UUID reservation but before directory mapping, a UUID object can be leaked. `GetVolumeGroupAttributes()` tolerates missing pool/object by logging and then reading from an empty values map, which can return empty attributes instead of a hard failure. Member mappings share the same OMAP namespace as metadata keys, so key naming collisions need discipline.

## Test Signals
No tests for this file are in the subset. Useful tests would cover group ID composition, stale reservation cleanup, creation time parse failures, member add/remove behavior, missing object behavior, namespace propagation, and concurrent reservation protection through caller locks.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/journal/volumegroupjournal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/aws_metadata.go -->
# sources/control-plane/ceph-csi/internal/kms/aws_metadata.go

## Purpose
`aws_metadata.go` registers the `aws-metadata` KMS provider, which uses AWS KMS to wrap per-volume DEKs and stores the encrypted DEK in volume metadata rather than in AWS.

## Important APIs, Types, And Functions
`awsMetadataKMS` stores Kubernetes secret lookup settings and AWS region, access key, secret key, optional session token, and CMK ARN. `initAWSMetadataKMS()` parses config and Kubernetes Secret data. `EncryptDEK()` calls AWS KMS `Encrypt` and base64-encodes the ciphertext. `DecryptDEK()` base64-decodes and calls AWS KMS `Decrypt`. `RequiresDEKStore()` returns `DEKStoreMetadata`. `getSecrets()` and `getService()` fetch credentials and build an AWS SDK client.

## Control Flow And State
Initialization reads an optional secret name from config, requires AWS region, fetches a Kubernetes Secret in the Ceph-CSI pod namespace, validates supported secret keys, and stores credential fields in memory. Each encrypt/decrypt operation creates a fresh AWS session and KMS client.

## State And Persistence Behavior
The provider does not persist DEKs in AWS; it expects the caller to store the returned encrypted blob in metadata. AWS credentials and CMK are held in process memory. `Destroy()` has no cleanup.

## Dependencies And Integration Points
The provider uses AWS SDK v1 session/credentials/KMS APIs and `internal/util/k8s.GetSecret`. It is selected by `GetKMS()` through provider registration in `kms.go`.

## Risks And Edge Cases
Creating a new session for each operation can add latency. `DecryptDEK()` does not specify a key ID, relying on ciphertext metadata. The secret parser rejects unknown keys, which is strict but can break shared Kubernetes Secrets. The code accepts an optional session token but does not refresh credentials.

## Test Signals
`aws_metadata_test.go` only asserts provider registration. There is no unit coverage for config parsing, Kubernetes Secret handling, AWS client construction, encryption/decryption, strict unknown-key rejection, or invalid base64.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/aws_metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/aws_metadata_test.go -->
# sources/control-plane/ceph-csi/internal/kms/aws_metadata_test.go

## Purpose
`aws_metadata_test.go` is a provider registration smoke test for the AWS metadata KMS backend.

## Important APIs, Types, And Functions
`TestAWSMetadataKMSRegistered` checks that `kmsManager.providers` contains `kmsTypeAWSMetadata`.

## Control Flow And Test Behavior
The test runs in parallel and uses `require.True` on the registry lookup result. Registration happens through the package-level `RegisterProvider` call in `aws_metadata.go`.

## Dependencies And Integration Points
The test depends on global package initialization order and the shared provider registry.

## Risks And Edge Cases
It does not instantiate the provider or mock Kubernetes/AWS dependencies. A provider can be registered but still fail all runtime configuration or encryption paths.

## Test Signals
The only signal is that static registration is wired. Runtime behavior needs separate tests around secrets, config, base64, and AWS API errors.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/aws_metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/aws_sts_metadata.go -->
# sources/control-plane/ceph-csi/internal/kms/aws_sts_metadata.go

## Purpose
`aws_sts_metadata.go` registers the `aws-sts-metadata` provider, which assumes an AWS IAM role via web identity before using AWS KMS to wrap DEKs stored in volume metadata.

## Important APIs, Types, And Functions
`awsSTSMetadataKMS` embeds `awsMetadataKMS` and adds a role ARN. `initAWSSTSMetadataKMS()` reads tenant-scoped Kubernetes Secret data for role ARN, CMK ARN, and region. `EncryptDEK()` and `DecryptDEK()` use a KMS client from `getServiceWithSTS()`. `getWebIdentityToken()` reads the OIDC token file. `getSecrets()` validates supported STS secret keys.

## Control Flow And State
Initialization sets the namespace to the tenant, resolves the secret name, fetches required Secret values, and stores role, CMK, and region. Per operation, `getServiceWithSTS()` reads the mounted OIDC token, calls STS `AssumeRoleWithWebIdentity`, converts temporary credentials into an AWS SDK v1 static credential set, and builds an AWS KMS client.

## State And Persistence Behavior
Encrypted DEKs are returned for metadata storage. Temporary STS credentials are not cached; they are requested per encrypt/decrypt operation. `Destroy()` behavior is inherited as no-op.

## Dependencies And Integration Points
This provider mixes AWS SDK v2 for STS with AWS SDK v1 for KMS. It depends on Kubernetes Secret access and the fixed token file `/run/secrets/tokens/oidc-token`.

## Risks And Edge Cases
Per-operation STS calls can be expensive and sensitive to token file availability. The code dereferences STS credential fields without nil checks. Unknown Kubernetes Secret keys are rejected. The error text for unsupported options references the AWS metadata provider name, not the STS provider name.

## Test Signals
`aws_sts_metadata_test.go` only validates provider registration. There is no coverage for token file errors, STS failures, secret parsing, temporary credential nil values, or AWS KMS behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/aws_sts_metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/aws_sts_metadata_test.go -->
# sources/control-plane/ceph-csi/internal/kms/aws_sts_metadata_test.go

## Purpose
`aws_sts_metadata_test.go` confirms that the AWS STS metadata KMS provider is registered during package initialization.

## Important APIs, Types, And Functions
`TestAWSSTSMetadataKMSRegistered` looks up `kmsTypeAWSSTSMetadata` in `kmsManager.providers`.

## Control Flow And Test Behavior
The test is parallel and performs a single registry assertion.

## Dependencies And Integration Points
It depends on the provider registration side effect in `aws_sts_metadata.go`.

## Risks And Edge Cases
Registration does not prove the provider can read OIDC tokens, assume a role, parse tenant Secrets, or call AWS KMS.

## Test Signals
The file provides static wiring coverage only. Provider initialization and STS/KMS paths remain untested here.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/aws_sts_metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/azure_vault.go -->
# sources/control-plane/ceph-csi/internal/kms/azure_vault.go

## Purpose
`azure_vault.go` registers the `azure-kv` KMS provider, which stores passphrases directly as Azure Key Vault secrets.

## Important APIs, Types, And Functions
`azureKMS` stores namespace, secret name, integrated DEK behavior, vault URL, client ID, tenant ID, and client certificate. `initAzureKeyVaultKMS()` parses config and Kubernetes Secret data. `FetchDEK()`, `StoreDEK()`, and `RemoveDEK()` call Azure Key Vault secret get, set, and delete APIs. `getService()` builds a certificate credential and Key Vault client.

## Control Flow And State
Initialization resolves a default or configured Kubernetes Secret name, requires vault URL, client ID, and tenant ID, then reads a client certificate from the Secret. Each DEK operation creates a fresh Azure credential and `azsecrets.Client` before calling the service.

## State And Persistence Behavior
The DEK/passphrase is persisted in Azure Key Vault under the supplied key. `integratedDEK` means no external metadata DEK store is required. Provider state keeps connection material in memory; `Destroy()` is no-op.

## Dependencies And Integration Points
The provider uses Azure SDK `azidentity` and `azsecrets`, plus Ceph-CSI Kubernetes Secret helpers. It is instantiated through the global KMS provider registry.

## Risks And Edge Cases
The certificate parser expects the Secret to contain certificate and private key material in a format accepted by Azure SDK. Each operation rebuilds the client. Delete behavior does not purge or wait for completion. Strict unknown-key rejection can reject shared Kubernetes Secrets. Error messages contain a repeated spelling typo in "secret" but still wrap failures.

## Test Signals
`azure_vault_test.go` only checks provider registration. Runtime paths around certificate parsing, Key Vault get/set/delete, config validation, and unknown Secret keys are not covered in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/azure_vault.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/azure_vault_test.go -->
# sources/control-plane/ceph-csi/internal/kms/azure_vault_test.go

## Purpose
`azure_vault_test.go` is a smoke test for Azure Key Vault KMS provider registration.

## Important APIs, Types, And Functions
`TestAzureKMSRegistered` verifies that `kmsTypeAzure` exists in `kmsManager.providers`.

## Control Flow And Test Behavior
The test runs in parallel and performs a single `require.True` assertion.

## Dependencies And Integration Points
It relies on package initialization executing the `RegisterProvider` call in `azure_vault.go`.

## Risks And Edge Cases
No provider initialization or Azure SDK behavior is tested. Registration can pass while all credential, Secret, or service interactions fail.

## Test Signals
The test proves only static provider wiring.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/azure_vault_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/dummy.go -->
# sources/control-plane/ceph-csi/internal/kms/dummy.go

## Purpose
`dummy.go` provides test-only KMS dummy provider registration utilities for code that needs an `EncryptionKMS` without contacting external systems.

## Important APIs, Types, And Functions
`TestDummyFunc` constructs an `EncryptionKMS`. `ProviderTest` describes a test provider. `kmsTestProviderList` holds registered test providers. `RegisterTestProvider()`, `GetKMSTestDummy()`, and `GetKMSTestProvider()` manage the test registry. `newDefaultTestDummy()` returns a `secretsKMS`; `newSecretsMetadataTestDummy()` returns a configured `secretsMetadataKMS`.

## Control Flow And State
Package initialization registers dummy providers for `metadata` and `default`. Lookups return nil when no matching dummy provider exists. The metadata dummy sets a test passphrase, tenant, and nil config.

## State And Persistence Behavior
The registry is a process-global map. Dummy KMS objects keep passphrases in memory and do not talk to Kubernetes or external KMS providers.

## Dependencies And Integration Points
The file depends on base64 encoding and the main KMS interfaces/types. It supports tests in other packages that need provider-shaped KMS values.

## Risks And Edge Cases
`RegisterTestProvider()` does not validate empty IDs, duplicate IDs, or nil constructors, unlike production `RegisterProvider()`. The global mutable map is not protected by a mutex. The dummy passphrases are hardcoded and unsuitable for production.

## Test Signals
No direct tests are in this subset. Indirect coverage occurs when other tests call the dummy registry. Useful coverage would assert missing lookup, duplicate behavior, and dummy encryption/decryption compatibility.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/dummy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/keyprotect.go -->
# sources/control-plane/ceph-csi/internal/kms/keyprotect.go

## Purpose
`keyprotect.go` registers the IBM Key Protect metadata KMS provider, which wraps DEKs with a configured customer root key and expects encrypted DEKs to be stored in volume metadata.

## Important APIs, Types, And Functions
`keyProtectKMS` stores namespace, Kubernetes Secret name, IBM Key Protect client, API key, CRK, service instance ID, URLs, region, session token, and optional CRK ARN. `initKeyProtectKMS()` parses config and Secret data. `EncryptDEK()` calls `client.Wrap` with volume ID as additional authenticated data. `DecryptDEK()` calls `client.Unwrap`. `RequiresDEKStore()` returns metadata storage. `getService()` builds a Key Protect client.

## Control Flow And State
Initialization resolves defaults for secret name, base URL, and token URL, requires service instance ID and root key credentials, and permits optional session token, region, and CRK ARN. Encrypt/decrypt build or replace the client before each operation, then base64 encode or decode wrapped bytes.

## State And Persistence Behavior
DEKs are persisted outside this provider as encrypted metadata. The provider holds credentials in memory. `Destroy()` is a no-op.

## Dependencies And Integration Points
The file depends on `github.com/IBM/keyprotect-go-client` and Kubernetes Secret helpers. It integrates with the shared KMS registry and `DEKStoreMetadata` workflow.

## Risks And Edge Cases
Per-operation client creation adds overhead. Strict Secret key validation can reject shared Secrets. Optional fields such as region/session token/CRK ARN are parsed but not used in `getService()`. Because volume ID is authenticated data, decrypting with a different volume ID should fail.

## Test Signals
`keyprotect_test.go` only validates registration. There is no coverage for config defaults, Secret parsing, client construction, wrap/unwrap, base64 errors, or AAD mismatch behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/keyprotect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/keyprotect_test.go -->
# sources/control-plane/ceph-csi/internal/kms/keyprotect_test.go

## Purpose
`keyprotect_test.go` confirms registration of the IBM Key Protect metadata KMS provider.

## Important APIs, Types, And Functions
`TestKeyProtectMetadataKMSRegistered` checks the global registry for `kmsTypeKeyProtectMetadata`.

## Control Flow And Test Behavior
The test is parallel and performs a single provider map lookup.

## Dependencies And Integration Points
It relies on package initialization in `keyprotect.go`.

## Risks And Edge Cases
No IBM client, configuration, Secret, or encryption behavior is exercised.

## Test Signals
The test covers static wiring only. Runtime provider paths require additional mocks or integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/keyprotect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/kmip.go -->
# sources/control-plane/ceph-csi/internal/kms/kmip.go

## Purpose
`kmip.go` registers the KMIP KMS provider. It can either ask a KMIP server to encrypt/decrypt DEKs through KMIP crypto RPCs or fetch a remote symmetric key and perform local AES-GCM encryption for metadata-stored DEKs.

## Important APIs, Types, And Functions
`kmipKMS` stores Kubernetes Secret lookup settings, endpoint, TLS config, unique key identifier, read/write timeouts, and `useCryptoRPC`. `initKMIPKMS()` parses config, Secret certificates, key identifier, TLS server name, and timeout options. Public KMS methods are `EncryptDEK`, `DecryptDEK`, `Destroy`, `RequiresDEKStore`, and `GetSecret`. Internal paths include `encryptDEKUsingEncryptRPC`, `decryptDEKUsingDecryptRPC`, `encryptDEKUsingRemoteKey`, `decryptDEKUsingRemoteKey`, `connect`, `discover`, `send`, `verifyResponse`, `getKey`, `symmetricEncrypt`, and `symmetricDecrypt`.

## Control Flow And State
Initialization builds a TLS 1.2 client config from CA, client certificate, and client key. `connect()` dials the KMIP endpoint, sets deadlines, performs TLS handshake, and verifies KMIP 1.4 support with a DiscoverVersions operation. `send()` constructs a single-batch KMIP request with a UUID batch item ID, TTLV-encodes it, writes to the connection, and decodes the response. `verifyResponse()` validates batch count, operation, batch item ID, and success status. Crypto RPC mode uses KMIP Encrypt/Decrypt with AES-CBC parameters and stores ciphertext plus nonce as JSON. Remote-key mode uses KMIP Get and local AES-GCM with a generated nonce.

## State And Persistence Behavior
The provider requires `DEKStoreMetadata`; encrypted DEK JSON is stored by callers. It does not cache KMIP connections or fetched keys. TLS and key identifiers stay in memory. `Destroy()` is no-op.

## Dependencies And Integration Points
The implementation uses `gemalto/kmip-go`, TLS/x509, Go crypto primitives, JSON encoding, Kubernetes Secrets, and helper functions from `kms_util.go`, `vault.go`, and `secretskms.go`.

## Risks And Edge Cases
KMIP operation support varies by server. The local-key mode exposes raw symmetric key material to the CSI process after a KMIP Get. Timeout config is parsed as int but stored as `uint8`, so large values can wrap. `AppendCertsFromPEM` return value is not checked. Crypto RPC mode uses AES-CBC with PKCS5 padding via the KMIP service, while local mode uses AES-GCM, so ciphertext formats are mode-specific. Network and KMIP response validation are only as strict as the decoded fields.

## Test Signals
`kmip_test.go` only checks registration. There is no coverage for TLS config validation, DiscoverVersions, TTLV request/response handling, crypto RPCs, local AES-GCM helpers, timeout conversion, malformed encrypted JSON, or KMIP error status mapping.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/kmip.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/kmip_test.go -->
# sources/control-plane/ceph-csi/internal/kms/kmip_test.go

## Purpose
`kmip_test.go` is a smoke test for KMIP KMS provider registration.

## Important APIs, Types, And Functions
`TestKMIPKMSRegistered` checks that `kmsTypeKMIP` is registered in `kmsManager.providers`.

## Control Flow And Test Behavior
The test runs in parallel and performs a single registry assertion.

## Dependencies And Integration Points
It depends on the registration side effect in `kmip.go`.

## Risks And Edge Cases
Registration does not validate certificates, KMIP endpoint compatibility, crypto RPC behavior, local-key encryption, or TTLV handling.

## Test Signals
Static provider wiring is covered; all runtime KMIP behavior is outside this test.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/kmip_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/kms.go -->
# sources/control-plane/ceph-csi/internal/kms/kms.go

## Purpose
`kms.go` is the KMS provider framework for Ceph-CSI encryption. It loads KMS configuration, resolves provider IDs, registers providers, instantiates KMS backends, and defines the core encryption and DEK-store interfaces.

## Important APIs, Types, And Functions
Key constants include `KMS_PROVIDER`, `encryptionKMSType`, `POD_NAMESPACE`, `KMS_CONFIGMAP_NAME`, `kmsConfigPath`, and `DefaultKMSType`. `GetKMS()` selects default or configured KMS instances. `getKMSConfiguration()` reads `/etc/ceph-csi-encryption-kms-config/config.json` or falls back to a Kubernetes ConfigMap. `getProvider()` accepts both old and new provider keys. `ProviderInitArgs`, `Provider`, `ProviderInitFunc`, and `kmsProviderList` implement registration/instantiation. `EncryptionKMS`, `DEKStoreType`, `DEKStore`, and `integratedDEK` define provider contracts.

## Control Flow And State
`GetKMS()` returns the default provider when `kmsID` is empty or `default`; otherwise it loads the config map/file, selects the named section, ensures it is a map, and calls `kmsManager.buildKMS()`. `buildKMS()` resolves the provider name, looks it up in the global registry, fills tenant/config/secrets and optional pod namespace, and calls the provider initializer. Providers self-register at package init time through `RegisterProvider()`.

## State And Persistence Behavior
The provider registry is a process-global mutable map. Configuration is read from a mounted file or live Kubernetes ConfigMap. No config is cached by this file; each `GetKMS()` loads configuration anew. `integratedDEK` returns plaintext values and signals that no external DEK store is needed.

## Dependencies And Integration Points
The file depends on JSON, environment variables, filesystem reads, and `internal/util/k8s`. It is used by volume encryption code to obtain an `EncryptionKMS` and optional `DEKStore` behavior.

## Risks And Edge Cases
`RegisterProvider()` panics on duplicate or incomplete providers, so init-time collisions are fatal. ConfigMap fallback couples CSI code directly to Kubernetes API access. `getKeys()` returns map keys in random order, which affects error message stability. `getPodNamespace()` absence is ignored during provider instantiation but can break providers that require namespace.

## Test Signals
`kms_test.go` covers registration panic for missing initializer and successful registration of a simple provider. It does not cover duplicate IDs, empty IDs, config file parsing, ConfigMap fallback, provider selection, default KMS instantiation, or `integratedDEK` behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/kms.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/kms_test.go -->
# sources/control-plane/ceph-csi/internal/kms/kms_test.go

## Purpose
`kms_test.go` verifies basic validation behavior for production KMS provider registration.

## Important APIs, Types, And Functions
`noinitKMS` is a minimal initializer used in tests. `TestRegisterProvider` checks that a provider without initializer panics and that a provider with a unique ID and initializer registers successfully.

## Control Flow And Test Behavior
The test runs subcases in a loop inside one parallel test. It uses `require.Panics` for invalid registration and `require.True` for successful registration.

## Dependencies And Integration Points
The test mutates the global `kmsManager.providers` map by registering `"initializer-only"`.

## Risks And Edge Cases
Because it mutates global registry state, repeated or reordered tests could collide if another test reuses the same ID. It does not test empty IDs or duplicate IDs.

## Test Signals
The file confirms one registration guard and a happy-path registration. Runtime KMS resolution and configuration loading are untested here.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/kms_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/kms_util.go -->
# sources/control-plane/ceph-csi/internal/kms/kms_util.go

## Purpose
`kms_util.go` provides a shared config conversion helper for integer options.

## Important APIs, Types, And Functions
`setConfigInt(option *int, config map[string]any, key string)` reads `key`, requires the JSON-decoded value to be `float64`, converts it to `int`, and stores it in `option`.

## Control Flow And State
Missing keys return an `errConfigOptionMissing`-wrapped error and leave the option unchanged. Non-`float64` values return `errConfigOptionInvalid`. Valid values update the pointed-to integer.

## State And Persistence Behavior
The function has no persistent state. It mutates only the caller-provided option pointer.

## Dependencies And Integration Points
The helper depends on error sentinels from `vault.go`. KMIP timeout parsing uses this helper because JSON config numbers decode to `float64`.

## Risks And Edge Cases
The conversion truncates fractional values without validation. It requires `float64`, so manually built configs using `int` fail even though the logical value is numeric. It does not check range before callers cast to narrower types.

## Test Signals
`kms_util_test.go` covers valid float64, invalid string, and missing key behavior. It does not cover fractional values, negative numbers, overflow, or nil option pointers.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/kms_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/kms_util_test.go -->
# sources/control-plane/ceph-csi/internal/kms/kms_util_test.go

## Purpose
`kms_util_test.go` tests the integer config conversion helper used by KMS providers.

## Important APIs, Types, And Functions
`TestSetConfigInt` defines table cases for valid, invalid, and missing values and calls `setConfigInt`.

## Control Flow And Test Behavior
Subtests run in parallel. The valid case supplies `1.0` and expects success. Error cases check `errors.Is` against `errConfigOptionInvalid` or `errConfigOptionMissing`.

## Dependencies And Integration Points
The test depends on KMS config error sentinels from `vault.go` and `testify/require`.

## Risks And Edge Cases
All cases share the same `option` variable pointer, and subtests run in parallel, which can race. The assertions for error cases check that the option is not equal to zero rather than checking it remained at its prior value.

## Test Signals
The test covers the common JSON-number path and two error categories. It does not cover fractional truncation, negative values, overflow, or parallel safety.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/kms_util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/secretskms.go -->
# sources/control-plane/ceph-csi/internal/kms/secretskms.go

## Purpose
`secretskms.go` implements the default Kubernetes-secret KMS and the `metadata` KMS that encrypts per-volume DEKs with a passphrase-derived key and stores encrypted DEKs in volume metadata.

## Important APIs, Types, And Functions
`secretsKMS` embeds `integratedDEK` and stores one passphrase from StorageClass secrets. `secretsMetadataKMS` stores `ProviderInitArgs` and implements metadata DEK encryption. `encryptedMetadataDEK` is JSON with encrypted DEK bytes and nonce. `newSecretsKMS`, `initSecretsMetadataKMS`, `FetchDEK`, `EncryptDEK`, `DecryptDEK`, `GetSecret`, `fetchEncryptionPassphrase`, `generateKeyFromPassphrase`, and `generateNonce` are the main functions.

## Control Flow And State
The default provider requires `encryptionPassphrase` in supplied secrets and returns that same passphrase for any key. The metadata provider first tries to fetch a user-provided Kubernetes Secret from configured name/namespace, falling back to StorageClass secrets when that config is missing. Encryption derives a 32-byte scrypt key from passphrase and volume ID, encrypts with `symmetricEncrypt`, and JSON-serializes the result. Decryption reverses the process with the same passphrase and volume ID.

## State And Persistence Behavior
`secretsKMS` stores no per-volume DEKs and performs no external writes. `secretsMetadataKMS` requires the caller to store encrypted DEK JSON in metadata. Passphrases are held in memory and may be fetched from tenant or StorageClass Kubernetes Secrets.

## Dependencies And Integration Points
This file uses Kubernetes Secret helpers, scrypt, random nonce generation, JSON, and symmetric helpers from `kmip.go`. It registers both the default and metadata providers with `kms.go`.

## Risks And Edge Cases
The passphrase and volume ID must be stable; changing either makes metadata DEKs undecryptable. Empty passphrases and salts are accepted by scrypt. User-provided Secret lookup depends on tenant namespace defaults. `StoreDEK` and `RemoveDEK` are no-ops for both providers, so callers must understand whether metadata storage is required.

## Test Signals
`secretskms_test.go` covers default passphrase requirement, nonce length, scrypt determinism and key length, metadata initialization, an encrypt/decrypt workflow, and registration. It does not cover Kubernetes user Secret fetching with mocked API failures, corrupted encrypted JSON, wrong volume IDs, or random nonce uniqueness statistically.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/secretskms.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/secretskms_test.go -->
# sources/control-plane/ceph-csi/internal/kms/secretskms_test.go

## Purpose
`secretskms_test.go` provides the most substantive KMS unit coverage in this subset, focused on default secrets KMS and metadata encryption helpers.

## Important APIs, Types, And Functions
Tests include `TestNewSecretsKMS`, `TestGenerateNonce`, `TestGenerateKeyFromPassphrase`, `TestInitSecretsMetadataKMS`, `TestWorkflowSecretsMetadataKMS`, and `TestSecretsMetadataKMSRegistered`.

## Control Flow And Test Behavior
The tests validate missing and present StorageClass passphrases, generated nonce length, deterministic scrypt output for varied inputs, metadata provider initialization, and a complete metadata KMS encrypt/decrypt workflow using in-memory secrets.

## Dependencies And Integration Points
The tests use `testify/require` and package-private helpers. They avoid Kubernetes API calls by using StorageClass secrets fallback rather than configured user Secret retrieval.

## Risks And Edge Cases
The workflow tests do not verify wrong volume ID or wrong passphrase failure. Empty passphrase and salt are explicitly accepted by the key derivation test, documenting current behavior. Random nonce uniqueness is not tested.

## Test Signals
The file gives meaningful confidence in local crypto helper wiring and metadata provider happy path. External Kubernetes Secret retrieval and malformed ciphertext handling remain uncovered.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/secretskms_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/vault.go -->
# sources/control-plane/ceph-csi/internal/kms/vault.go

## Purpose
`vault.go` implements the base HashiCorp Vault KMS provider using Kubernetes service account authentication and stores passphrases directly in Vault.

## Important APIs, Types, And Functions
`vaultConnection` stores the libopenstorage secrets client, Vault config map, key context, and destroy-key behavior. `vaultKMS` embeds `vaultConnection` and `integratedDEK`, adding `vaultPassphrasePath`. Helpers include `setConfigString`, `setConfigBoolean`, `initConnection`, `initCertificates`, `connectVault`, `getDeleteKeyContext`, and `detectAuthMountPath`. Provider methods include `initVaultKMS`, `FetchDEK`, `StoreDEK`, and `RemoveDEK`.

## Control Flow And State
`initConnection()` validates and merges Vault address, backend, backend path, destroy behavior, TLS server name, namespaces, CA verification, and key context. `initCertificates()` writes a CA certificate from supplied secrets into a temporary file and adds its path to Vault config. `initVaultKMS()` configures Kubernetes auth mount path, role, passphrase root/path, service-account token path, connects to Vault, and returns the provider.

## State And Persistence Behavior
DEKs/passphrases are stored as Vault secrets with shape `data.passphrase`, often under a configured passphrase path. Temporary certificate files are removed by `Destroy()`. Delete context can request hard destroy for KV-v2-style secrets.

## Dependencies And Integration Points
The file depends on HashiCorp Vault API constants, libopenstorage secrets/vault integration, temporary file helpers, and the shared KMS provider registry. Tenant-aware Vault variants reuse `vaultConnection`.

## Risks And Edge Cases
Connection config is a mutable map reused across parse layers, so partial updates can persist. Temp certificate files must be cleaned by `Destroy()`. `setConfigBoolean()` expects string booleans, not native JSON booleans. The provider assumes Vault secret payloads use nested `data.passphrase`; incompatible backends fail at read time.

## Test Signals
`vault_test.go` covers selected config parsing and auth mount path behavior. It does not connect to Vault, validate certificate temp file cleanup, exercise Fetch/Store/Remove, or test all configuration merge paths.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/vault.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/vault_sa.go -->
# sources/control-plane/ceph-csi/internal/kms/vault_sa.go

## Purpose
`vault_sa.go` implements the `vaulttenantsa` provider, a tenant-aware Vault KMS that authenticates to Vault using a ServiceAccount from the tenant namespace.

## Important APIs, Types, And Functions
`vaultTenantSA` embeds `vaultTenantConnection` and stores tenant ServiceAccount name plus temporary token directory. `initVaultTenantSA()` handles legacy config transformation, base Vault config, tenant overrides, ServiceAccount token path setup, certificate setup, and Vault connection. Methods include `Destroy`, `configureTenant`, `parseConfig`, `isTenantSAConfigOption`, `setServiceAccountName`, `getToken`, `getTokenPath`, and `createToken`.

## Control Flow And State
Initialization sets defaults for tenant config name, tenant ServiceAccount name, auth mount path, and Vault role. Tenant config can override allowed options globally, from nested tenant config, and from the tenant ConfigMap. `getToken()` first tries the Kubernetes TokenRequest API through `createToken()`, then falls back to legacy ServiceAccount referenced token Secrets. `getTokenPath()` writes the token to a temporary `0600` file and points Vault Kubernetes auth at it.

## State And Persistence Behavior
The provider creates a temporary token directory and removes it in `Destroy()`. Passphrases are stored in Vault through inherited `vaultTenantConnection` methods. Tenant-specific config is held in mutable Vault config/key-context maps.

## Dependencies And Integration Points
This provider uses Kubernetes ServiceAccount, Secret, and token APIs through Ceph-CSI helpers, libopenstorage Vault auth settings, and shared Vault tenant config parsing from `vault_tokens.go`.

## Risks And Edge Cases
Temporary token cleanup depends on `Destroy()`. TokenRequest failures fall back to legacy Secrets, but both paths require Kubernetes RBAC. Tenant ConfigMaps are filtered by `isTenantSAConfigOption`; unsupported keys are silently ignored. ServiceAccount tokens written to disk must remain protected by filesystem permissions and lifecycle.

## Test Signals
`vault_sa_test.go` checks provider registration and tenant SA config parsing. It does not exercise TokenRequest, legacy token Secret fallback, temp token path creation, Vault connection, or cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/vault_sa.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/vault_sa_test.go -->
# sources/control-plane/ceph-csi/internal/kms/vault_sa_test.go

## Purpose
`vault_sa_test.go` verifies static registration and configuration parsing for the Vault tenant ServiceAccount provider.

## Important APIs, Types, And Functions
`TestVaultTenantSAKMSRegistered` checks the provider registry. `TestTenantSAParseConfig` exercises `vaultTenantSA.parseConfig()` and related tenant-specific options.

## Control Flow And Test Behavior
The tests instantiate provider structs directly and validate configured fields and Vault auth settings after parsing sample maps.

## Dependencies And Integration Points
The tests depend on shared Vault config helper behavior and provider registration from `vault_sa.go`.

## Risks And Edge Cases
They do not mock Kubernetes ServiceAccounts or tokens and do not establish Vault connections. Temp token file handling and RBAC failures remain untested.

## Test Signals
The tests cover static wiring and selected option parsing. Authentication and external service behavior remain integration-test concerns.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/vault_sa_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/vault_test.go -->
# sources/control-plane/ceph-csi/internal/kms/vault_test.go

## Purpose
`vault_test.go` validates selected helper behavior for the base Vault KMS provider.

## Important APIs, Types, And Functions
The tests cover configuration helpers such as `setConfigString`, `setConfigBoolean`, `initConnection`, and `detectAuthMountPath`, plus provider registration for `vault`.

## Control Flow And Test Behavior
The tests build in-memory config maps, call package-private helpers, and assert resulting values or errors. They avoid live Vault and Kubernetes dependencies.

## Dependencies And Integration Points
The file depends on Vault config constants and the package global registry. It exercises shared helpers used by base Vault and tenant-aware providers.

## Risks And Edge Cases
Because it avoids Vault connections, it cannot catch backend payload shape, auth, or network failures. It also does not prove temporary certificate files are cleaned up.

## Test Signals
The tests provide useful coverage for option parsing and auth mount path derivation. Fetch/store/remove and live provider initialization remain outside this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/vault_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/vault_tokens.go -->
# sources/control-plane/ceph-csi/internal/kms/vault_tokens.go

## Purpose
`vault_tokens.go` implements the `vaulttokens` provider, a tenant-aware Vault KMS where each tenant supplies a Vault token through a Kubernetes Secret. It also converts legacy Vault environment-style config into Ceph-CSI JSON config.

## Important APIs, Types, And Functions
`standardVault` models legacy `VAULT_*` keys. `vaultTokenConf` models Ceph-CSI config keys and `convertStdVaultToCSIConfig()`. `transformConfig()` converts legacy maps. `vaultTenantConnection` holds common tenant config, while `vaultTokensKMS` adds `TokenName`. Main methods are `initVaultTokensKMS`, `FetchDEK`, `StoreDEK`, `RemoveDEK`, `configureTenant`, `init`, `parseConfig`, `setTokenName`, `initCertificates`, `getToken`, `getCertificate`, `isTenantConfigOption`, `parseTenantConfig`, `setTenantAuthNamespace`, and `fetchTenantConfig`.

## Control Flow And State
Initialization optionally transforms legacy ConfigMap format, initializes Vault connection config, applies defaults, parses global config, applies nested tenant and tenant ConfigMap overrides, fetches the tenant token from a Secret, initializes certificates from tenant or CSI namespace fallback, and connects to Vault. Tenant ConfigMaps are filtered to allow only selected Vault connection options. Fetch/store/remove delegate to libopenstorage secrets using the tenant key context.

## State And Persistence Behavior
Vault tokens are read from Kubernetes Secrets and stored in memory as `api.EnvVaultToken`. CA and client certificate material can be written to temp files and later removed through inherited `Destroy()`. Passphrases are persisted in Vault as nested `data.passphrase` objects.

## Dependencies And Integration Points
The file depends on HashiCorp Vault API env keys, libopenstorage secrets, Kubernetes ConfigMap/Secret helpers, temporary file helpers, and base Vault connection code. `vault_sa.go` reuses the tenant connection and config filtering pattern.

## Risks And Edge Cases
`fetchTenantConfig()` only accepts `map[string]map[string]any`, which may not match maps produced by generic JSON unmarshal without additional conversion. Tenant ConfigMap unsupported options are silently ignored. Certificate fallback uses pod namespace from environment. Token retrieval requires the `token` key. Multiple parse layers mutate the same config maps, so precedence must be tested carefully.

## Test Signals
`vault_tokens_test.go` covers config parsing, provider initialization failure paths, legacy transform behavior, default transform values, registration, and tenant auth namespace override logic. It does not connect to Vault, fetch real Kubernetes Secrets/ConfigMaps, or exercise certificate temp file cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/vault_tokens.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/vault_tokens_test.go -->
# sources/control-plane/ceph-csi/internal/kms/vault_tokens_test.go

## Purpose
`vault_tokens_test.go` validates tenant-token Vault configuration conversion, parsing, registration, and namespace override semantics.

## Important APIs, Types, And Functions
Tests include `TestParseConfig`, `TestInitVaultTokensKMS`, `TestStdVaultToCSIConfig`, `TestTransformConfig`, `TestTransformConfigDefaults`, `TestVaultTokensKMSRegistered`, and `TestSetTenantAuthNamespace`.

## Control Flow And Test Behavior
The tests construct in-memory Vault config maps and structs, call conversion/parsing helpers, and assert resulting fields. Initialization tests focus on expected errors without live external services.

## Dependencies And Integration Points
The file exercises shared `vaultConnection` parsing, tenant connection config, legacy environment-key conversion, and provider registry state.

## Risks And Edge Cases
The tests do not establish Vault connections or mock Kubernetes token/certificate retrieval. Map type assumptions for nested tenants and ConfigMap data are only partially covered.

## Test Signals
The suite gives good confidence in config transformations and default handling. Runtime behavior around tokens, certificates, Vault reads/writes, and delete semantics remains uncovered here.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/kms/vault_tokens_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/liveness/liveness.go -->
# sources/control-plane/ceph-csi/internal/liveness/liveness.go

## Purpose
`liveness.go` implements the Ceph-CSI liveness sidecar logic. It probes the CSI driver over gRPC and exposes a Prometheus gauge indicating readiness.

## Important APIs, Types, And Functions
`liveness` is a Prometheus gauge named `csi_liveness`. `getLiveness(timeout, csiConn)` sends a CSI Probe RPC and updates the gauge. `recordLiveness(endpoint, drivername, pollTime, timeout)` registers metrics, connects to the CSI endpoint, and probes periodically. `Run(conf)` starts polling and the metrics server.

## Control Flow And State
`Run()` launches `recordLiveness()` in a goroutine and then starts the metrics HTTP server. `recordLiveness()` registers the gauge, opens a CSI connection using csi-lib-utils metrics manager, then loops on a ticker. Each probe uses a timeout-bound context. Probe errors or not-ready responses set the gauge to zero; ready responses set it to one.

## State And Persistence Behavior
State is process-local Prometheus metric state. There is no disk persistence. The gRPC connection is held for the life of the liveness process.

## Dependencies And Integration Points
The file uses Kubernetes CSI lib-utils `connection`, `metrics`, and `rpc`, Prometheus client, gRPC, and Ceph-CSI config/logging/metrics server helpers. It runs as an auxiliary liveness process for CSI components.

## Risks And Edge Cases
`prometheus.Register` failure is fatal, so duplicate registration in the same process kills liveness. `connlib.Connect` is expected to retry forever; a returned error is treated as fatal misconfiguration. The first gauge update does not occur until the first ticker tick.

## Test Signals
No tests are included in this subset. Useful tests would mock Probe responses, duplicate registration, connection failure, timeout behavior, and gauge updates.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/liveness/liveness.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/controller/controllerserver.go -->
# sources/control-plane/ceph-csi/internal/nfs/controller/controllerserver.go

## Purpose
`controllerserver.go` implements the NFS CSI controller by delegating storage operations to CephFS and adding NFS export creation, deletion, and mutable server metadata.

## Important APIs, Types, And Functions
`Server` embeds `csi.UnimplementedControllerServer` and stores a CephFS backend controller. `NewControllerServer()` initializes global CephFS volume/snapshot journals and the backend controller. Controller methods include capability validation, `CreateVolume`, `DeleteVolume`, publish/unpublish, expand, snapshot create/delete, and `ControllerModifyVolume`.

## Control Flow And State
`CreateVolume()` forces `backingSnapshot=false`, creates the CephFS backend volume, builds admin credentials, opens an `NFSVolume`, connects to Ceph, creates an NFS export, adds `share` to the volume context, and optionally applies mutable parameters. `DeleteVolume()` validates the ID, connects an `NFSVolume`, deletes the export while tolerating not-found, then delegates backend volume deletion. Most other CSI methods delegate directly to CephFS or return no-op success.

## State And Persistence Behavior
Persistent state includes the CephFS backing volume, NFS-Ganesha export, and journal attributes such as NFS cluster/server metadata. The controller updates global `store.VolJournal` and `store.SnapJournal` for CephFS RADOS namespace.

## Dependencies And Integration Points
The server integrates CSI protobufs, CephFS controller, CephFS store/journal utilities, NFS type helpers, Ceph-CSI credentials, and gRPC status codes. It bridges CephFS subvolume creation with NFS export publication.

## Risks And Edge Cases
`CreateVolume()` mutates `req.Parameters` directly and assumes the map is non-nil. If export creation succeeds but later `ControllerModifyVolume()` fails, cleanup is not performed in this method. Delete maps most NFS export errors to `InvalidArgument`, which may obscure backend or transient failures. Global journal assignment can affect tests or multiple driver instances.

## Test Signals
No controller tests are included in this subset. Desired coverage includes nil parameter maps, backend create cleanup, export already-exists/not-found behavior, mutable server update failure after export creation, and delegation status mapping.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/controller/controllerserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/driver/driver.go -->
# sources/control-plane/ceph-csi/internal/nfs/driver/driver.go

## Purpose
`driver.go` wires the NFS CSI driver process. It creates the CSI driver descriptor, registers capabilities, selects controller/node/identity servers, starts gRPC, and optionally enables profiling.

## Important APIs, Types, And Functions
`nfsDriver` implements `driver.Driver`. `NewDriver()` returns a new driver instance. `Run(conf)` is the main entrypoint.

## Control Flow And State
`Run()` creates a common CSI driver with driver name, version, node ID, instance ID, and fencing setting. Controller capabilities and volume access modes are added when running controller or combined mode. It builds a nonblocking gRPC server and always installs identity. Depending on config, it installs node, controller, or both servers, starts the gRPC server with middleware options, optionally starts metrics/profiling goroutines, and waits.

## State And Persistence Behavior
The file does not persist data itself. It initializes long-lived server objects and process-level gRPC/metrics/profiling state.

## Dependencies And Integration Points
It integrates common CSI server infrastructure, NFS controller/node/identity packages, driver config, feature gates, logging, and Prometheus/profiling helpers.

## Risks And Edge Cases
Mode selection uses a switch where node mode wins over controller mode if both booleans are true; combined mode is reached only when neither flag is set. Capability registration is skipped for pure node mode. Fatal logging exits the process on CSI driver initialization failure.

## Test Signals
No tests are present in this subset. Useful coverage would verify server selection, capability sets, node/controller combined behavior, profiling startup, and feature gate propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/driver/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/identity/identityserver.go -->
# sources/control-plane/ceph-csi/internal/nfs/identity/identityserver.go

## Purpose
`identityserver.go` implements the NFS CSI identity server by wrapping the common default identity server and declaring controller-service plugin capability.

## Important APIs, Types, And Functions
`Server` embeds `*csicommon.DefaultIdentityServer`. `NewIdentityServer(d)` constructs the wrapper. `GetPluginCapabilities()` returns CSI `CONTROLLER_SERVICE` capability.

## Control Flow And State
Construction delegates default identity behavior to common CSI code. `GetPluginCapabilities()` ignores request contents and returns a static capability list.

## State And Persistence Behavior
No persistent state is managed here. The server holds only the embedded common identity server.

## Dependencies And Integration Points
The file uses CSI protobuf types and common Ceph-CSI identity support. It is installed by the NFS driver in all modes.

## Risks And Edge Cases
Only controller service capability is advertised explicitly here; other identity behavior comes from the default server. If future plugin capabilities are needed, this static list must be updated.

## Test Signals
No tests are included in this subset. A simple unit test could assert the returned capability list and default identity metadata.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/identity/identityserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/nodeserver/nodeserver.go -->
# sources/control-plane/ceph-csi/internal/nfs/nodeserver/nodeserver.go

## Purpose
`nodeserver.go` implements the NFS CSI node service. It validates publish requests, resolves NFS mount sources, optionally reads updated server metadata from the CephFS journal, mounts NFS exports, unmounts targets, and reports filesystem stats.

## Important APIs, Types, And Functions
`NodeServer` embeds `csicommon.DefaultNodeServer`. `NewNodeServer()` initializes the CephFS volume journal and default node server. CSI methods include `NodePublishVolume`, `NodeUnpublishVolume`, `NodeGetCapabilities`, and `NodeGetVolumeStats`. Helpers include `mountNFS`, `validateNodePublishVolumeRequest`, `getSource`, and `getServerFromVolume`.

## Control Flow And State
`NodePublishVolume()` validates the request, enforces service account restrictions, builds mount options including read-only mode, resolves the source as `server:share`, optionally resolves a network namespace path from cluster ID, and mounts. `mountNFS()` creates the target directory if absent, returns success if already mounted, then either runs `mount` through `nsenter` or uses the Kubernetes mounter. `getSource()` prefers journal-stored server metadata when credentials are supplied, falls back to volume context `server`, formats IPv6 in brackets, and requires `share`.

## State And Persistence Behavior
Node-side state is the mounted filesystem target. Server override state can be persisted in the CephFS volume journal by controller modify operations. The node does not persist its own metadata.

## Dependencies And Integration Points
The node server integrates CSI protobufs, Kubernetes mount utils, network utilities, CephFS journal/store setup, NFS volume metadata, service account restriction validation, net namespace config, and common filesystem stats.

## Risks And Edge Cases
Invalid credentials in `getServerFromVolume()` are ignored and cause fallback to volume context, which favors availability but can hide metadata access failures. Mount stderr with zero exit status is treated as an error. The mount option append produces `-o` followed by each option as separate args only in nsenter path; the direct mounter receives the raw slice. Error classification relies partly on substring matching.

## Test Signals
`nodeserver_test.go` covers publish request validation and source formatting for hostnames, IPv4, IPv6, missing server, and missing share. It does not cover real mount/unmount, net namespace mounting, service account restrictions, journal server overrides, stats, or error mapping.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/nodeserver/nodeserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/nodeserver/nodeserver_test.go -->
# sources/control-plane/ceph-csi/internal/nfs/nodeserver/nodeserver_test.go

## Purpose
`nodeserver_test.go` validates lightweight NFS node helper behavior without performing real mounts.

## Important APIs, Types, And Functions
`Test_validateNodePublishVolumeRequest` covers request field validation. `Test_getSource` covers source construction from `server` and `share` volume context values.

## Control Flow And Test Behavior
The validation test uses `staticVolume=true` for the happy path to bypass normal CSI volume ID format validation. Source tests construct minimal publish requests and compare returned source strings or error presence.

## Dependencies And Integration Points
The tests use CSI protobuf structs and the NFS `ParameterServer` constant. They call package-private helpers directly.

## Risks And Edge Cases
`getSource()` can call `getServerFromVolume()` when secrets are present, but tests omit secrets and therefore skip journal lookup. Mounting, unmounting, service account restrictions, and stats are not exercised.

## Test Signals
The tests confirm required request fields and IPv6 bracket formatting. They leave integration-heavy behavior to other tests or manual validation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/nodeserver/nodeserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/types/errors.go -->
# sources/control-plane/ceph-csi/internal/nfs/types/errors.go

## Purpose
`errors.go` defines shared sentinel errors for the NFS controller/type package so callers can classify connection and not-found failures.

## Important APIs, Types, And Functions
`ErrNotConnected` signals missing Ceph/NFS connection state. `ErrNotFound` is the parent not-found sentinel. `ErrExportNotFound` wraps `ErrNotFound` for missing exports. `ErrFilesystemNotFound` wraps `ErrNotFound` for missing filesystems.

## Control Flow And State
There is no control flow beyond package-level error construction. The wrapping structure is designed for `errors.Is(err, ErrNotFound)` checks.

## State And Persistence Behavior
The file has no persistent or mutable state.

## Dependencies And Integration Points
It depends on Go `errors` and `fmt`. `controller.DeleteVolume`, `NFSVolume.DeleteExport`, and attribute helpers use these sentinels for error classification.

## Risks And Edge Cases
The wrapped errors include static text, so callers should use `errors.Is` rather than string matching. Some code still uses string matching for go-ceph errors before converting to these sentinels.

## Test Signals
No tests are included. Useful tests would assert `errors.Is(ErrExportNotFound, ErrNotFound)` and `errors.Is(ErrFilesystemNotFound, ErrNotFound)`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/types/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/types/volume.go -->
# sources/control-plane/ceph-csi/internal/nfs/types/volume.go

## Purpose
`volume.go` defines `NFSVolume`, the controller-side helper that connects a CSI volume ID to CephFS, Ceph Manager NFS export APIs, and CephFS journal metadata for NFS configuration.

## Important APIs, Types, And Functions
`NFSVolume` stores context, volume ID, cluster ID, monitors, filesystem ID, object UUID, credentials, connection state, and cluster connection. Public methods include `NewNFSVolume`, `String`, `Connect`, `Destroy`, `GetExportPath`, `CreateExport`, `DeleteExport`, `SetServer`, and `GetServer`. Internal helpers include `createExportCommand`, `deleteExportCommand`, `getAttribute`, `setAttribute`, `getNFSCluster`, and `setNFSCluster`.

## Control Flow And State
`NewNFSVolume()` decomposes a CSI ID into cluster, location/filesystem ID, and object UUID. `Connect()` loads monitors from CSI config and establishes a go-ceph cluster connection. `CreateExport()` stores the NFS cluster in the journal, builds a CephFS export spec from backend volume context, calls go-ceph NFS admin, and falls back to `ceph nfs export create` for older Ceph errors. `DeleteExport()` reads the stored NFS cluster, removes the export through go-ceph NFS admin, and falls back to CLI deletion for unsupported API paths. Attribute helpers resolve filesystem and metadata pool, connect the CephFS journal, and store/fetch prefixed attributes.

## State And Persistence Behavior
Persistent state includes NFS exports in Ceph Manager/Ganesha and journal attributes in RADOS OMAP: NFS cluster name and optional server. The helper holds an active cluster connection only between `Connect()` and `Destroy()`. Export path is deterministic as `/<volumeID>`.

## Dependencies And Integration Points
The file uses go-ceph NFS admin APIs, CSI volume context, CephFS core and store packages, global `store.VolJournal`, Ceph-CSI credentials, monitor config, CLI execution fallback, and NFS error sentinels.

## Risks And Edge Cases
Methods require `Connect()` first and return `ErrNotConnected` otherwise. The code depends on backend volume context keys like `fsName`, `nfsCluster`, and `subvolumePath`. Fallback behavior matches error strings from go-ceph/Ceph, which can be brittle. The expression in `getAttribute()` combines `&&` and `||` without parentheses, so `util.ErrKeyNotFound` can match regardless of the first condition; this is probably intended but easy to misread.

## Test Signals
No direct tests for this file are in the subset. High-value tests would mock filesystem lookup, metadata pool lookup, journal store/fetch, NFS admin create/remove, fallback CLI paths, export already-exists/not-found cases, and connection lifecycle.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/nfs/types/volume.go -->
