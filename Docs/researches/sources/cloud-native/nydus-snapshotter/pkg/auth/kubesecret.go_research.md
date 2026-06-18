# sources/cloud-native/nydus-snapshotter/pkg/auth/kubesecret.go

Purpose: implements a Kubernetes Secret-backed registry credential provider by watching all `kubernetes.io/dockerconfigjson` secrets and searching their Docker config auth entries by registry host.

Important APIs and functions: package globals `kubeSecretListener` and `configMu`; `KubeSecretProvider` implements `AuthProvider` and `RenewableProvider`; `InitKubeSecretListener` builds a Kubernetes client and starts secret synchronization; `KubeSecretListener.addDockerConfig`, `deleteDockerConfig`, `SyncKubeSecrets`, and `GetCredentialsStore` manage the watched Docker config map.

Control flow: initialization is idempotent under `configMu`, optionally checks the kubeconfig path, loads client config with client-go, builds a clientset, and starts a shared informer. The informer lists/watches all namespaces for Docker config JSON secrets, adding/updating parsed Docker config files by namespace/name key and deleting on secret deletion. `GetCredentials` parses the image host and asks the listener for the first config with complete username/password auth.

State and persistence: all watched secret auth data is held in memory in `dockerConfigs`. `configMu` guards the global listener pointer and the map. The Kubernetes API is the persistent source of truth.

Dependencies and integration points: uses client-go `SharedIndexInformer`, corev1 Secret types, Docker configfile parsing, and `parseReference`. It is included in both normal and renewable provider chains because the informer can observe updates.

Risks: `InitKubeSecretListener` assigns the global listener before all setup succeeds, so a failed config/client/sync path can leave a non-nil but partially initialized listener. The kubeconfig existence log message has inverted wording for `os.IsNotExist`. `DeleteFunc` assumes direct objects and does not handle tombstones. It returns the first matching config from map iteration, which is nondeterministic if multiple secrets match the same host.

Test signals: `kubesecret_test.go` manually adds a Docker config secret object, validates provider lookup, direct store lookup, map insertion, deletion, and nil after deletion.
