# sources/control-plane/longhorn/chart/templates/storageclass.yaml

Purpose: optionally creates a ConfigMap containing the default Longhorn StorageClass manifest for Longhorn Manager or install logic to apply.

Important APIs/types/functions: Kubernetes `ConfigMap`, `.Values.persistence.createStorageClass`, embedded `storageclass.yaml`, StorageClass `storage.k8s.io/v1`, provisioner `driver.longhorn.io`, default-class annotation, volume expansion, reclaim policy, volume binding mode, replica count, stale replica timeout, filesystem/mkfs parameters, migratable, NFS options, backing image parameters, recurring job selector, data locality, disk/node/share-manager selectors, tolerations, unmap behavior, revision counter, data engine, and backup target name.

Control flow: if enabled, the template emits one ConfigMap. Inside it, StorageClass parameters are always or conditionally inserted based on persistence values. The actual StorageClass is not a top-level resource in this template; it is stored as a YAML string.

State and persistence: the ConfigMap persists desired StorageClass YAML. The eventual StorageClass influences persistent volume provisioning, reclaim behavior, replica count, data engine, and backup target linkage.

Dependencies/integration: depends on Longhorn Manager or install routines that read the `longhorn-storageclass` ConfigMap and create/update the real StorageClass. It ties directly to values in `values.yaml` and to CSI driver deployment from `deployment-driver.yaml`.

Risks: because the StorageClass is embedded YAML, template quoting mistakes can produce a ConfigMap that renders but later fails when applied. `recurringJobSelector` stringification of a list is sensitive to JSON/YAML formatting. Backing image parameters are not quoted, so null or complex strings must be tested carefully. The `dataEngine` parameter is nested under the `disableRevisionCounter` condition, so disabling that value can also omit dataEngine.

Test signals: render with createStorageClass false/true, custom annotations, backing image enabled, recurring job selector, selectors/tolerations, v2 data engine, and empty optional fields. Parse the embedded `storageclass.yaml` and validate it with `kubectl apply --dry-run=server`.
