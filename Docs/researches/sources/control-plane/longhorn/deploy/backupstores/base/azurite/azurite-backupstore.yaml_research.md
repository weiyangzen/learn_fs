# sources/control-plane/longhorn/deploy/backupstores/base/azurite/azurite-backupstore.yaml

Purpose: provides a Kustomize base for a test Azure Blob-compatible backupstore using Azurite plus a placeholder Longhorn credential secret.

Important APIs/types/functions: Kubernetes `Secret` `azblob-secret` in `longhorn-system`, `apps/v1` `Deployment` `longhorn-test-azblob` in `default`, container image `mcr.microsoft.com/azure-storage/azurite:3.33.0`, container port 10000, and `Service` `azblob-service` with `sessionAffinity: ClientIP`.

Control flow: applying the manifest creates an empty credential secret for Longhorn and a single Azurite pod exposed by a ClusterIP service on port 10000. Users or tests must populate secret data and configure Longhorn's backup target to point at the service.

State and persistence: the Azurite deployment has no volume, so blob data is container-local/ephemeral and lost when the pod is replaced. The secret is persistent but initially has empty data.

Dependencies/integration: depends on the Azurite image, Kubernetes DNS for `azblob-service.default`, and Longhorn backup target configuration using Azure-compatible credentials in `longhorn-system`. The paired kustomization includes this file.

Risks: this is not production durable because no persistent volume backs Azurite. Empty secret data means Longhorn backups will fail until credentials/certs are populated. Service lives in `default` while the Longhorn secret lives in `longhorn-system`, so namespace assumptions are fixed.

Test signals: `kubectl apply -k` should create the deployment, service, and secret. Populate secret data, set Longhorn backup target to the Azurite endpoint, create a backup, restore it, and verify data disappears after deleting/recreating the Azurite pod.
