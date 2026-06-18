<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/config.py -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/config.py

## Purpose
`config.py` centralizes environment-derived settings, constants, logging, and global cleanup registries for JuiceFS CSI Driver GitHub CI e2e scripts.

## Important APIs, Types, and Functions
It exports constants such as `KUBE_SYSTEM`, `META_URL`, `ACCESS_KEY`, `SECRET_KEY`, `STORAGE`, `BUCKET`, `TOKEN`, `JUICEFS_MODE`, `IS_CE`, `Beta`, `MOUNT_MODE`, `RESOURCE_PREFIX`, `IN_CCI`, `CCI_APP_IMAGE`, `CCI_MOUNT_IMAGE`, `IN_VCI`, `GLOBAL_MOUNTPOINT`, `SECRET_NAME`, `STORAGECLASS_NAME`, `FS_NAME`, and `CONFIG_NAME`. It configures logger `LOG`. Mutable lists `SECRETs`, `STORAGECLASSs`, `DEPLOYMENTs`, `JOBs`, `PODS`, `PVCs`, and `PVs` track created Kubernetes objects for test cleanup.

## Control Flow, State, and Persistence
All behavior occurs at import time by reading environment variables and configuring logging. There is no file persistence; state is in module globals shared by `model.py`, `util.py`, and tests. `RESOURCE_PREFIX` combines mount mode and JuiceFS mode, so all model-created resources get predictable per-mode names.

## Dependencies and Integration Points
It depends on Python `os` and `logging`, the CI environment, JuiceFS credentials/secrets, and optional CCI/VCI settings. It is imported by `model.py`, `e2e-test.py`, and related test helpers.

## Risks and Test Signals
Risks include importing with missing environment variables producing empty credential fields, `TEST_MODE` access without a default causing errors if unset, and module-level mutable lists being shared across tests. Signals are resource names and logs reflecting expected mode, plus successful cleanup by consumers of the global lists.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/config.py -->
