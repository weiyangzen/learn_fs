# sources/control-plane/csi-driver-smb/charts/v1.19.1/csi-driver-smb/templates/storageclass.yaml

## Purpose
This template renders zero or more SMB `StorageClass` objects for chart `v1.19.1` from `.Values.storageClasses`. It lets chart users ship provisioner-ready classes with SMB share parameters instead of applying separate manifests.

## Important APIs, Types, And Functions
The Kubernetes API is `storage.k8s.io/v1/StorageClass`. Helm loops over `.Values.storageClasses`, emits `metadata.name`, common SMB labels, optional annotations, optional `parameters`, `reclaimPolicy`, `volumeBindingMode`, `allowVolumeExpansion`, and optional `mountOptions`. The provisioner is always `$.Values.driver.name`.

## Control Flow
The whole file is skipped when `.Values.storageClasses` is unset or empty. Within each item, `reclaimPolicy` defaults to `Delete`, `volumeBindingMode` defaults to `Immediate`, and `allowVolumeExpansion` defaults to true unless the key is explicitly present.

## State And Persistence Behavior
Rendered StorageClasses are persistent cluster objects. They do not hold SMB credentials directly unless users place secret references in `parameters`; PVCs created later bind to these classes and inherit mount options such as `noserverino`.

## Dependencies And Integration Points
The class must match the `CSIDriver`/controller provisioner name and the controller RBAC must allow StorageClass reads plus secret access for provisioner and node-stage secrets. Parameters integrate with external SMB shares and Kubernetes Secrets.

## Risks And Test Signals
Risks include exposing incorrect secret namespaces, omitting required SMB mount options, or accidentally making the class default through annotations. Test by templating example `storageClasses`, creating PVCs against each class, checking PV parameters, testing expansion, and validating mount options on Linux/Windows nodes.
