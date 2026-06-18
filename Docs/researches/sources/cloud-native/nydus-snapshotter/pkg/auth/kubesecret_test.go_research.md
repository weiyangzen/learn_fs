# sources/cloud-native/nydus-snapshotter/pkg/auth/kubesecret_test.go

Purpose: verifies the in-memory Docker config parsing and lookup behavior used by the Kubernetes secret provider.

Important APIs and functions: `testDockerConfigJSONFmt` builds a Docker config JSON secret payload; `TestGetCredentialsStore` calls `InitKubeSecretListener`, manually invokes `addDockerConfig`, calls `NewKubeSecretProvider().GetCredentials`, calls `GetCredentialsStore`, and then deletes the config.

Control flow: the test tolerates `InitKubeSecretListener(ctx, "")` failure because local hosts may not have kubeconfig, but still expects `kubeSecretListener` to be non-nil. It then inserts a fake `corev1.Secret` with `.dockerconfigjson` data and checks registry auth retrieval.

State and persistence: uses package-global `kubeSecretListener`; inserted config is removed at the end. It does not reset the whole global listener.

Dependencies and integration points: directly exercises Docker configfile parsing and `KubeSecretProvider.GetCredentials` with production reference parsing.

Risks and gaps: because init errors are ignored and the global listener may persist across tests, the test is sensitive to package-level state. It does not exercise the informer, Kubernetes fake client, update/delete event handlers, missing data keys, invalid config JSON, or multiple matching secrets.

Test signals: confirms a valid dockerconfigjson secret can provide username/password and that deletion removes the store entry.
