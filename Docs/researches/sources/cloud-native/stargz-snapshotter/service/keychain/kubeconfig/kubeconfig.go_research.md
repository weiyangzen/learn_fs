<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/kubeconfig/kubeconfig.go -->
# sources/cloud-native/stargz-snapshotter/service/keychain/kubeconfig/kubeconfig.go

## Purpose
Implements a Kubernetes-secret-backed resolver credential provider by watching all `kubernetes.io/dockerconfigjson` secrets visible through a kubeconfig.

## Important APIs, Types, And Functions
- `WithKubeconfigPath` sets an explicit kubeconfig path.
- `NewKubeconfigKeychain` returns a `resolver.Credential` closure.
- `newKeychain` initializes immediately or waits asynchronously for a missing kubeconfig file.
- `initialize` loads client config, creates a Kubernetes client, and starts secret sync.
- `startSyncSecrets`, `runWorker`, and `processItem` maintain a map of parsed Docker config files.
- `credentials` scans cached configs for a host, with Docker Hub alias handling.

## Control Flow
Startup either initializes immediately or polls every 10 seconds for the configured kubeconfig. The informer lists/watches Docker config JSON secrets in all namespaces, queues add/update/delete keys, synchronizes existing items, and runs a worker that updates or removes cached config entries.

## State And Persistence
The keychain keeps an in-memory `map[namespace/name]*ConfigFile`. Persistent source state is Kubernetes Secret data. Cache lifetime follows the process and context cancellation.

## Dependencies And Integration Points
Depends on client-go informers, workqueues, Kubernetes CoreV1 secrets, Docker config parsing, and resolver credential chaining. It integrates with cluster image pull secrets independently of CRI PullImage.

## Risks And Edge Cases
Requires broad secret list/watch permissions. Missing kubeconfig is tolerated, but invalid kubeconfig disables syncing. Only dockerconfigjson secrets are supported; legacy dockercfg is a TODO. Credential selection scans map iteration order, so overlapping host credentials are nondeterministic.

## Test Signals
Signals include delayed initialization after kubeconfig appears, add/update/delete secret cache changes, Docker Hub alias matching, identity-token precedence, and anonymous behavior when no matching secret exists.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/keychain/kubeconfig/kubeconfig.go -->
