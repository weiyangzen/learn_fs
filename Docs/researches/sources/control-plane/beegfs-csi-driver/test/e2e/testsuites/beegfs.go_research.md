<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/testsuites/beegfs.go -->
# sources/control-plane/beegfs-csi-driver/test/e2e/testsuites/beegfs.go

Purpose: BeeGFS-specific storage e2e suite layered on Kubernetes storage framework patterns.
Important APIs/functions: `beegfsTestSuite`, `InitBeegfsTestSuite`, `DefineTests`, setup/cleanup closures, and Ginkgo specs for multi-filesystem access, stripe pattern parsing, invalid pool handling, RDMA, host filesystem read-only protection, permissions, delete scoping, fallback timing, and 200-volume bulk performance.
Control flow/state: each spec initializes a `BeegfsDriver`, prepares a framework config, creates `VolumeResource` objects, and records them for cleanup. Some specs mutate driver StorageClass params; the slow serial fallback spec mutates live plugin config and restores it at the end.
Dependencies/integration: uses Kubernetes e2e pod/PV helpers, BeeGFS `beegfs-ctl`, FSExec host commands, driver ConfigMap/CR update helpers, and labels selecting controller/node pods.
Risks/test signals: concurrent bulk create can leak non-namespaced resources if goroutines fail before resource tracking; serial config mutation can disturb parallel tests if labels are ignored; timing assertions are environment-sensitive. Strong signals include explicit output checks for `beegfs-ctl`, permission mode/owner checks, tar diff validation, and creation/deletion timing bounds.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/testsuites/beegfs.go -->
