# sources/control-plane/mayastor/test/python/k8s/fio.yaml

## Purpose
Kubernetes manifest for running fio against multiple Mayastor PVCs.

## Important APIs, Types, And Functions
Defines a `ConfigMap` named `fiomap` containing `fio.conf` and a `Pod` named `fio` using image `mayadata/fio`. It mounts PVCs `ms-1` through `ms-6` and the fio config.

## Control Flow
When applied, Kubernetes creates the config map and pod; the pod runs `fio /config/fio.conf` and exits.

## State And Persistence
The fio job writes `vol.test` files under mounted PVC paths. The pod is `restartPolicy: Never`; PVC and ConfigMap lifecycle are managed by tests.

## Dependencies And Integration Points
Used by `test_pvc.py` through Kubernetes Python utilities. Integrates with default namespace PVCs, Mayastor storage classes, and fio verification settings.

## Risks
The config defines jobs for volume-1 through volume-4 but mounts six PVCs; dynamic manifest code may cover six elsewhere. PVC names are hard-coded.

## Test Signals
A succeeded fio pod validates PVC binding, filesystem mounts, and IO correctness with crc32 verification.
