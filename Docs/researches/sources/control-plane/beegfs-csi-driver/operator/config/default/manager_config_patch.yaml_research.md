<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/default/manager_config_patch.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/default/manager_config_patch.yaml

## Purpose
Optional patch to mount controller-runtime `ControllerManagerConfig` into the manager deployment.

## Important APIs, Types, And Functions
Adds `--config=controller_manager_config.yaml`, mounts a `manager-config` ConfigMap at `/controller_manager_config.yaml`, and defines the volume.

## Control Flow
Only applies when uncommented in the default kustomization. The manager binary then reads component config on startup.

## State And Persistence
No independent state; uses a generated ConfigMap from `config/manager/kustomization.yaml`.

## Dependencies And Integration Points
Depends on `manager-config` ConfigMap and controller-runtime component config support.

## Risks And Edge Cases
Currently inactive. If enabled, command-line flags and component config can conflict, and mount path/subPath must match the binary argument.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/default/manager_config_patch.yaml -->
