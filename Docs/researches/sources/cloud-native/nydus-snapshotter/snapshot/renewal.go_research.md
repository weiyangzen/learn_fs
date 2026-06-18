<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/renewal.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/renewal.go

Purpose: periodically renews registry credentials for live RAFS instances and hot-reloads changed credentials into running nydusd daemons.

Important APIs: `startCredentialRenewal`, `credentialRenewalLoop`, and `reconcileCredentials`. `startCredentialRenewal` initializes the auth credential store, performs an immediate reconciliation, logs startup, and launches a ticker goroutine.

Control flow and state: reconciliation walks managers, then running daemons, then their RAFS instances. For each instance with an image reference, it marks the ref live, renews credentials through `auth.RenewCredential`, compares old/new base64 credentials, and calls `d.UpdateAuthConfig(snapshotID, kc)` when changed. After scanning, `auth.EvictStaleCredentials(live)` removes store entries not backed by a live RAFS instance.

Dependencies/integration: depends on manager daemon caches populated by filesystem recovery, daemon running states, auth credential store, and nydusd auth hot-reload API.

Risks and test signals: manager and daemon list methods must be concurrency-safe because the goroutine runs in the background. Hot reload failures are logged but do not stop renewal. Credential comparison via base64 assumes stable serialization. `renewal_test.go` only covers lifecycle with an empty manager list.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/renewal.go -->
