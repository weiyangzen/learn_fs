<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/secrets.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/secrets.go

**Purpose:** Retrieves Kubernetes Secrets and contains an unfinished/disabled secret cache implementation with informer-based invalidation/update.

**Important APIs and types:** `cachedSecret` stores stringified data. `secretCache` has a map, RW mutex, and atomic running flag. Internal methods include `cacheKey`, `startSecretWatcher`, `deleteFromCache`, and `updateCache`. Exported `GetSecret` fetches a secret directly from the API server. An unnamed function `_` contains the cache-aware path but is not callable by normal code.

**Control flow, state, and persistence:** `GetSecret` always creates/uses a Kubernetes client, fetches the named secret with `context.TODO`, converts byte values to strings, and returns a new map. The cache path, if renamed/enabled, would start a shared informer once, hash namespace/name into a 16-byte SHA-256 prefix key, update only already-cached entries on informer updates unless forced, delete on informer deletes, and stop on SIGINT/SIGTERM.

**Dependencies and integration points:** Depends on Kubernetes corev1, informers, cache utilities, OS signals, atomics, SHA-256, and logging. It integrates with CSI secret retrieval for credentials and KMS configuration.

**Risks and test signals:** The active exported path has no cache and no caller context. The disabled cache has an explicit FIXME about memory growth and uses process signal handling internally. Secret values are converted to strings and held in memory. No direct tests in this subset cover direct retrieval or cache behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/secrets.go -->
