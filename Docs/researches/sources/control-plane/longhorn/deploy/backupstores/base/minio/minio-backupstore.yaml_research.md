# sources/control-plane/longhorn/deploy/backupstores/base/minio/minio-backupstore.yaml

Purpose: provides a Kustomize base for a test S3-compatible backupstore using MinIO plus placeholder AWS-style credentials/certificates.

Important APIs/types/functions: `Secret` `minio-secret` in `default` and `longhorn-system`, `Deployment` `longhorn-test-minio`, image `minio/minio:RELEASE.2022-02-01T18-00-14Z`, `emptyDir` storage, certificate secret volume keys `AWS_CERT` and `AWS_CERT_KEY`, env keys `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, command creating `/storage/backupbucket` and certificate symlinks, container port 9000, and `Service` `minio-service`.

Control flow: applying the manifest creates empty secrets, starts MinIO with a pre-created `backupbucket`, mounts TLS material from the secret, reads root credentials from the same secret, and exposes port 9000 through a service with ClientIP session affinity.

State and persistence: object data is stored on `emptyDir` and is lost with pod replacement. Secrets are persistent but initially empty and must contain credentials and TLS certificate data.

Dependencies/integration: depends on the pinned MinIO image, secret keys, Kubernetes DNS for `minio-service.default`, and Longhorn backup target configuration using the `longhorn-system` secret. The server pod reads credentials from the `default` secret.

Risks: empty secret data prevents container startup or TLS setup. The old MinIO image may have compatibility or security issues. Ephemeral storage makes this useful for tests only. TLS symlink setup assumes the secret keys exist and match MinIO cert naming requirements.

Test signals: populate both namespace secrets with access key, secret key, cert, and cert key; apply the base; verify MinIO health and bucket creation; configure Longhorn S3 backup target; run backup/restore; recreate the pod to confirm ephemeral data behavior.
