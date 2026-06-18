# sources/control-plane/longhorn/scripts/generate-backupstore-credentials.sh

## Purpose
Bash generator for Longhorn backupstore credential Kustomize overlays under `deploy/backupstores/overlays/generated-credentials`. It supports `azurite`, `cifs`, `minio`, `nfs`, and `all`, producing secret patch YAMLs and per-backend `kustomization.yaml` files.

## Important APIs, Functions, and Data
Top-level environment inputs include Azure blob variables, CIFS credentials, AWS/S3-compatible credentials, optional TLS cert/key values, and `AWS_ENDPOINTS`. `SUPPORTED_BACKENDS` drives `all` generation.

Functions: `check_env_or_fail` validates required environment variables; `generate_all_overlay` writes an aggregate Kustomization referencing all backends; `generate_backend` dispatches to backend-specific generators; `generate_azurite_backend`, `generate_cifs_backend`, `generate_minio_backend`, and `generate_nfs_backend` write overlays; `generate_patch_with_ns` writes Kubernetes `Secret` patches; `b64`, `fail_if_base64_encoded`, and `is_base64` handle base64 behavior.

## Control Flow
The entry point parses `--no-encode` and one backend argument. It reports base64 mode, then either iterates all supported backends and writes the aggregate overlay or writes a single backend. Each credential backend removes and recreates its target directory before generating files. MinIO validates `AWS_ENDPOINTS` differently depending on base64 mode and requires cert/key when the decoded or raw endpoint is HTTPS.

## State and Persistence
The script destructively replaces backend output directories with generated Kubernetes YAML. Secrets are persisted in generated files, base64-encoded by default or written as supplied with `--no-encode`. No cluster state is changed directly.

## Dependencies and Integration Points
Depends on Bash, GNU/coreutils-like `base64`, and the Longhorn repo layout. Outputs are Kustomize overlays that reference `deploy/backupstores/base/<backend>` and secret names such as `azblob-secret`, `cifs-secret`, and `minio-secret` in `longhorn-system` and sometimes `default` namespaces.

## Risks
Generated files may contain live credentials. `is_base64` treats many short strings as valid base64, so double-encode protection can reject legitimate plaintext. `rm -rf "${TARGET_DIR:?}"` is guarded but still destructive within the generated credentials tree. In `--no-encode` mode the script expects already-base64 values but only decodes `AWS_ENDPOINTS` for HTTPS detection, not every secret value.

## Test Signals
Run with dummy credentials for each backend and assert expected files exist, YAML parses, and Kustomize can build each overlay. Test `--no-encode` with known base64 values and HTTPS/non-HTTPS endpoints. Confirm no generated credentials are accidentally committed.
