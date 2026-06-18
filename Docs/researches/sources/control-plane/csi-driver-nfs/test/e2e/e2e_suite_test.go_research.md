## sources/control-plane/csi-driver-nfs/test/e2e/e2e_suite_test.go

Purpose: bootstraps and tears down the NFS CSI e2e suite. It configures Kubernetes e2e flags, ensures `KUBECONFIG` exists, creates an in-process NFS CSI driver and controller server, installs an NFS server plus Helm driver deployment, and registers the Ginkgo suite.

Important APIs and globals include storage parameter maps for default, zero mount permissions, subDir, retain, archive, and archive subDir modes; `testCmd`; `execTestCmd`; `handleFlags`; `TestMain`; `TestE2E`; and `convertToPowershellCommandIfNecessary`. `BeforeSuite` runs `make install-nfs-server` and `make e2e-bootstrap`, then starts `nfsDriver.Run(false)` in a goroutine. `AfterSuite` prints logs, tears down Helm, and tests install/uninstall scripts.

State includes environment variables `NODE_ID`, `TEST_WINDOWS`, `KUBECONFIG`, a unix socket under `/tmp`, and cluster resources installed by make targets. Risks include process-wide `os.Chdir`, goroutine lifetime after tests, hard-coded NFS service DNS name, and shell command failures aborting the suite. Test signal is the full integration lifecycle.
