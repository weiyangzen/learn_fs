# sources/control-plane/rook/pkg/operator/k8sutil/configmap_test.go

Purpose: tests ConfigMap deletion, operator-setting loading, and create-or-update behavior.

Important APIs/types/functions: `TestDeleteConfigMap`, `TestGetOperatorSetting`, and `TestCreateOrUpdateConfigMap`.

Control flow: deletion test creates a ConfigMap, calls `DeleteConfigMap` with wait and timeout error enabled, then asserts a later get returns NotFound. Operator setting test checks default before config load, env override, configmap load into env, unset handling after load, missing setting default, and env override for another key. Create/update test creates a ConfigMap through helper, verifies data, mutates input data, calls helper again, and verifies updated data.

State and persistence behavior: fake Kubernetes client persists ConfigMaps. Tests mutate process env via `t.Setenv` and `os.Unsetenv`.

Dependencies/integration: uses client-go fake client, Kubernetes API error helpers, and testify.

Risks: package-global `loadedOperatorSettings` can leak between tests in the same package. Tests do not cover owner references on create/update, retrieval errors other than NotFound, or labels/annotations preservation.

Test signals: good coverage for core user-facing behavior: settings precedence and idempotent ConfigMap updates.
