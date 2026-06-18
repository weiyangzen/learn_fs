# sources/control-plane/rook/pkg/operator/k8sutil/deployment_test.go

Purpose: exercises multi-deployment update and rollout-wait helpers with fake clients and controlled list functions.

Important APIs/types/functions: `TestUpdateMultipleDeploymentsAndWait`, `TestUpdateMultipleDeployments`, `TestWaitForDeploymentsToUpdate`, `Test_maxInt32Ptr`, `newInt32`, and `createDeploymentOrDie`.

Control flow: the integration test updates three deployments, leaves one unchanged, includes one missing deployment, and simulates one progress-deadline failure and one timeout. `TestUpdateMultipleDeployments` verifies empty inputs, successful updates, no-change skip behavior, progress deadline aggregation, and missing-deployment failures. `TestWaitForDeploymentsToUpdate` uses list functions that advance status over calls or return errors to cover success, timeout, never-listed deployment, list failure, and progress deadline exceeded.

State and persistence behavior: fake clientset stores deployments; a reactor records update actions. Package global wait period/timeout are temporarily shortened and restored.

Dependencies/integration: uses client-go fake/reactor APIs, Kubernetes deployment statuses/conditions, and testify.

Risks: tests cover the multi-update path but not `UpdateDeploymentAndWait`, image lookup, owner reference discovery, delete deployment, label helpers, create/update deployment, or cronjob helpers.

Test signals: strong coverage of the rollout waiting algorithm and failure aggregation for batch deployment updates.
