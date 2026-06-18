## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/storageclass.yaml

Purpose: optionally renders one or more StorageClass objects from `.Values.storageClasses`. By default the values file comments out examples, so no StorageClass is created unless users configure the list.

Important behavior: for each item it sets name, shared chart labels, optional annotations, provisioner from `.Values.driver.name`, arbitrary parameters, default reclaim policy `Delete`, default volumeBindingMode `Immediate`, default `allowVolumeExpansion: true` unless explicitly set, and optional mountOptions.

State is cluster-scoped StorageClass resources. Dependencies include SMB driver name, user-provided secret names/namespaces, SMB source paths, and mount options. Risks include leaking credential references into chart values, unsafe mount options, default expansion enabled, and multiple releases trying to manage the same StorageClass names. Test signal is Helm render plus actual dynamic provisioning behavior.
