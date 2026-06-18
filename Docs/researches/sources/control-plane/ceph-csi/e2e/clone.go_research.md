# sources/control-plane/ceph-csi/e2e/clone.go

Purpose: contains a shared clone-size validation helper for e2e tests that need to verify cloning a PVC into a larger PVC and then mounting the clone in an application.

Important APIs/types/functions: `validateBiggerCloneFromPVC(f, pvcPath, appPath, pvcClonePath, appClonePath)` loads source PVC/app YAML, forces the source PVC to `1Gi`, creates the source PVC and app, loads the clone PVC/app YAML, points the clone `DataSource.Name` at the source PVC, forces the clone request to `2Gi`, creates the clone and app, deletes the source pair, and validates the clone size.

Control flow: the helper creates the source workload with a stable app label used for later pod selection, then creates the clone workload with the same label. After deleting the parent PVC/app, it branches on `VolumeMode`: filesystem clones are checked through `checkDirSize()`, while block-mode clones are checked through `checkDeviceSize()`. It then deletes the clone workload.

State and persistence: creates two PVC/app pairs in the framework namespace and relies on CSI clone provisioning to create backend state. It expects deleting the parent after clone creation not to invalidate the clone. No durable state should remain after `deletePVCAndApp()` calls complete.

Dependencies and integration points: uses `loadPVC()`, `loadApp()`, `createPVCAndApp()`, `deletePVCAndApp()`, `checkDirSize()`, and `checkDeviceSize()` from the e2e helper set, Kubernetes core resource quantity parsing, and framework namespace state. CephFS invokes this for larger PVC-to-PVC clone coverage.

Risks: clone and app use the same label selector, so concurrent same-namespace callers could select unexpected pods. The function calls `logAndFail()` on clone load failures instead of returning errors consistently. It assumes the clone template has a non-nil data source and that the clone can be larger than the parent.

Test signals: passing signals are successful clone provisioning, successful source deletion after clone creation, observed `2Gi` filesystem directory or block device size in the clone app, and final cleanup without leftover PVC/PV/app resources.
