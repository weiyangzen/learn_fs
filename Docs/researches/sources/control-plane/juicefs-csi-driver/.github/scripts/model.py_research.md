<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/model.py -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/model.py

## Purpose
`model.py` defines Python Kubernetes object wrappers used by JuiceFS CSI Driver e2e tests. It turns common test resources into create/delete/watch helper classes while registering created objects in global cleanup lists from `config.py`.

## Important APIs, Types, and Functions
Classes are `Secret`, `StorageClass`, `PVC`, `PV`, `Deployment`, `Job`, and `Pod`. `Secret` creates CE or EE secret data and can wait for webhook `initconfig` injection or read owner references. `StorageClass` creates a CSI storage class with JuiceFS secret refs, mount options, resource parameters, and expansion enabled. `PVC` creates claims, updates capacity, checks deletion/bind state, and resolves bound volume IDs. `PV` creates static CSI persistent volumes with `juicefs/mount-*` attributes and secret refs. `Deployment`, `Job`, and `Pod` create Ubuntu or cloud-provider app workloads that continuously or once write timestamps into mounted PVCs, with CCI/VCI labels/annotations and resources when configured.

## Control Flow, State, and Persistence
Each `create` method builds Kubernetes Python client objects and submits them to `CoreV1Api`, `StorageV1Api`, `AppsV1Api`, or `BatchV1Api`, then appends `self` to the appropriate global list (`SECRETs`, `STORAGECLASSs`, `PVCs`, `PVs`, `DEPLOYMENTs`, `JOBs`, `PODS`). Delete methods call Kubernetes delete APIs and remove the instance from the list. Watch methods use polling or `watch.Watch().stream` for secret injection, job completion, pod readiness, and pod deletion. Kubernetes cluster resources are the durable state; module globals are in-process cleanup state.

## Dependencies and Integration Points
The file depends on the Kubernetes Python client, `watch`, `ConflictError`, base64 encoding, `time`, and config globals for credentials, namespaces, resource prefixes, images, and environment mode. It is consumed by `test_case.py` and e2e orchestration to create dynamic/static volume resources and workloads against the deployed CSI driver.

## Risks and Test Signals
Risks include mutable default argument `pvcs=[]`, fragile readiness logic requiring all pod conditions true, incomplete conflict handling in `Deployment.update_replicas` if exceptions lack `reason`, no timeouts in some API reads beyond watch stream limits, base64-secret construction with empty environment values, and object-list cleanup desynchronization if Kubernetes delete fails. Signals are Kubernetes API success, owner-reference/initconfig checks, job completion, pod ready/delete watch events, PVC bound state, and PV/PVC volume-handle reads.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/model.py -->
