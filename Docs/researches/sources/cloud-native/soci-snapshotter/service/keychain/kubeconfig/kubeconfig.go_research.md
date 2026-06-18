# sources/cloud-native/soci-snapshotter/service/keychain/kubeconfig/kubeconfig.go

Purpose: Kubernetes secret-backed credential provider that watches `kubernetes.io/dockerconfigjson` secrets and serves registry credentials to resolver code.

Important APIs/types/functions: `WithKubeconfigPath`, `NewKubeconfigKeychain`, `newKeychain`, `keychain.credentials`, `startSyncSecrets`, `runWorker`, and `processNextItem`. `dockerconfigSelector` selects Docker config JSON secrets.

Control flow: a background goroutine optionally waits for a kubeconfig file, loads Kubernetes client config, creates a clientset, starts a shared informer for dockerconfigjson secrets across all namespaces, queues add/update/delete keys, waits for cache sync, then processes queued keys. Existing secrets are parsed into Docker config files; deleted secrets remove cached configs. Credential lookup normalizes Docker Hub and scans cached config files for matching host credentials.

State and persistence: in-memory map from namespace/name secret key to Docker config file, guarded by mutex. Informer and workqueue are initialized after kubeconfig/client setup. No persistence beyond Kubernetes API state.

Dependencies/integration points: used by plugin when kubeconfig keychain is enabled. Depends on client-go informers, workqueue, Docker configfile parser, containerd reference specs, and resolver credential function type.

Risks: kubeconfig file updates are not watched after initial load. The selector is assigned to `FieldSelector` even though secret type is usually a field/label nuance; if unsupported, list/watch may fail. Credential lookup scans all namespaces and may return the first matching secret without namespace/image scoping. Queue processing logs parse errors but does not retry.

Test signals: no direct tests here; Kubernetes-backed auth needs integration/e2e coverage.
