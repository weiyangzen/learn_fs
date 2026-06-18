<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/renewal_test.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/renewal_test.go

Purpose: smoke-tests credential renewal goroutine startup and cancellation.

Important test: `TestStartCredentialRenewalLifecycle` creates a cancellable test context, starts renewal with a 30 ms interval and an empty manager list, sleeps long enough for several ticks, cancels, then gives the goroutine time to observe cancellation.

Control flow and state: because managers are empty, `reconcileCredentials` is a no-op except credential-store initialization/eviction behavior.

Dependencies/integration: uses Go testing context and manager type only.

Risks and test signals: this is a lifecycle smoke test, not a behavioral credential renewal test. It does not assert hot-reload calls, stale eviction contents, running-state filtering, or changed-vs-unchanged credential handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/renewal_test.go -->
