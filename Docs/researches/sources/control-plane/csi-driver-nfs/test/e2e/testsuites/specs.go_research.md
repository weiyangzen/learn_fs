## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/specs.go

Purpose: provides declarative test input structs and setup methods that translate scenario data into StorageClasses, PVCs, Pods, Deployments, inline CSI volumes, raw block devices, and subPath mounts.

Important types are `PodDetails`, `VolumeMode`, `VolumeMountDetails`, `VolumeDeviceDetails`, `DataSource`, and `VolumeDetails`. Important methods include `SetupDynamicPersistentVolumeClaim`, `SetupWithDynamicVolumes`, `SetupWithCSIInlineVolumes`, `SetupDeployment`, `SetupWithDynamicMultipleVolumes`, and `SetupWithDynamicVolumesWithSubpath`.

State is the cleanup function list returned to caller and Kubernetes resources created through `testsuites.go` helpers. Dependencies include the e2e driver interface, storage/v1 binding modes, core/v1 typed data sources, and Ginkgo logging. Risks include one StorageClass per volume, limited data source fields, binding-mode paths that skip PV validation for WaitForFirstConsumer until pod use, and inline volumes ignoring the provided driver instance. Test signal is indirect but central because every dynamic provisioning scenario uses these builders.
