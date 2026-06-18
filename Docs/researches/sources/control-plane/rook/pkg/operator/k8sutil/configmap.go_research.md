# sources/control-plane/rook/pkg/operator/k8sutil/configmap.go

Purpose: utility functions for ConfigMap deletion, create/update, and loading operator settings from the operator config ConfigMap into environment variables.

Important APIs/types/functions: package variable `loadedOperatorSettings`, `DeleteConfigMap`, `CreateOrUpdateConfigMap`, `GetOperatorSetting`, and `ApplyOperatorSettingsConfigmap`.

Control flow: `DeleteConfigMap` adapts ConfigMap delete/get operations to generic `DeleteResource` with foreground, zero-grace deletion defaults. `CreateOrUpdateConfigMap` gets by name, creates on NotFound, or updates existing Data and OwnerReferences. `GetOperatorSetting` warns when settings are read before the configmap load flag is set, then returns an environment value if present or the provided default. `ApplyOperatorSettingsConfigmap` reads `rook-ceph-operator-config` in `POD_NAMESPACE`, sets each data key into process env, and marks settings loaded even when the ConfigMap is absent.

State and persistence: writes ConfigMaps and process environment variables. `loadedOperatorSettings` is process-global state that affects warnings only.

Dependencies/integration: depends on client-go CoreV1 ConfigMaps, generic `DeleteResource`, Kubernetes NotFound errors, and env var constants from k8sutil.

Risks: setting configmap data into environment mutates global process state and can affect tests or later reconciles. Existing labels/annotations are not updated in `CreateOrUpdateConfigMap`, only data and owner refs. `GetOperatorSetting` cannot distinguish unset from intentionally empty env values because `LookupEnv` returns true for empty strings.

Test signals: `configmap_test.go` covers delete with wait, env/default/configmap precedence, configmap application, and create/update data mutation.
