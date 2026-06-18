# sources/control-plane/mayastor/test/python/k8s/test_pvc.py

## Purpose
Async pytest coverage for Kubernetes Mayastor pool, PVC, and fio workflows.

## Important APIs, Types, And Functions
Defines Kubernetes helpers `get_api`, `create_msp`, `delete_msp`, `create_pvc`, `delete_pvc`, `wait_for_it`, `wait_until_gone`, `watch_for`, `fio_delete`, `fio_from_yaml`, `create_fio_manifest`, and test `test_msp`.

## Control Flow
The test loads kube config, creates MayastorPool custom resources, creates PVCs against a storage class, waits for Bound/Running/Succeeded phases, runs fio from either static YAML or generated manifests, and deletes resources.

## State And Persistence
State is Kubernetes CRDs, PVCs, ConfigMaps, Pods, and Mayastor-backed volumes. Cleanup deletes PVC/fio resources but depends on cluster behavior for finalizers.

## Dependencies And Integration Points
Depends on the Kubernetes Python client, dynamic client, watch API, asyncio, `yaml`, and local `fio.yaml`. Integrates with Mayastor CRDs and storage classes.

## Risks
Cluster-specific names, namespaces, storage classes, and CRD schema can break tests. The watch/wait loops use fixed iteration counts and sleep behavior, and `assert event["object"].status.phase, "Succeeded"` appears to assert truthiness rather than equality.

## Test Signals
PVC Bound state, fio pod Succeeded state, and MayastorPool online status provide end-to-end Kubernetes control-plane and datapath signals.
