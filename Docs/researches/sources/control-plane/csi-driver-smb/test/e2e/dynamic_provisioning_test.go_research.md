<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/dynamic_provisioning_test.go -->
# sources/control-plane/csi-driver-smb/test/e2e/dynamic_provisioning_test.go

Purpose: Ginkgo e2e suite for SMB CSI dynamic provisioning behavior across Linux and Windows clusters.

Important APIs/tests: The suite creates a privileged Kubernetes e2e framework namespace, checks driver pod restarts before each test, initializes `SMBDriver`, and runs many testsuites: restart-driver volume creation (currently skipped), command/write-read dynamic volume, collocated pods, read-only volume, delete pod and remount, reclaim policy delete/retain, multiple volumes, subpath, clone, retain/archive on delete policies, resize, and CSI inline volumes with copied secrets.

Control flow: Each `ginkgo.It` constructs `testsuites.PodDetails`, `VolumeDetails`, storage class parameters, expected pod commands, and then calls the relevant testsuite `Run`. Windows handling is explicit through `convertToPowershellCommandIfNecessary`, `isWindowsCluster`, `winServerVer`, and skip helpers. Inline volume tests copy an SMB secret into the test namespace and clean it up with defer.

State and persistence behavior: Creates real Kubernetes StorageClasses, PVCs, PVs, pods/deployments, secrets, SMB backing directories/shares, and may restart the driver daemonset in the skipped test. Cleanup is delegated to testsuites.

Dependencies and integration points: Depends on the Kubernetes e2e framework, Ginkgo v2, pod security admission labels, package-level suite globals from `suite_test.go`, SMB driver object builders, and many test suite helpers.

Risks: Tests require a fully configured cluster, SMB server/secret environment, and OS-specific command behavior. Some test names include `[Windows]` even when they may skip Windows or run with Windows conversions. External issue-linked scenarios encode regression intent and can be environment-sensitive.

Test signals: This is the high-level integration signal that dynamic provisioning, mounting, reclaim policies, subdir handling, cloning, expansion, and inline volumes work end to end.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/dynamic_provisioning_test.go -->
