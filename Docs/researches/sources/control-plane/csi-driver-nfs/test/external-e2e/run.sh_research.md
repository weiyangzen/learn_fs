## sources/control-plane/csi-driver-nfs/test/external-e2e/run.sh

Purpose: runs Kubernetes external storage e2e tests against the NFS CSI driver under an alternate driver name. It installs Ginkgo, downloads Kubernetes v1.24.0 e2e binaries, installs the driver and NFS server, then invokes `e2e.test` with the external testdriver manifest.

Important flow: `setup_e2e_binaries` downloads and extracts `kubernetes-test-linux-amd64.tar.gz`, sets Helm overrides for `test.csi.k8s.io`, rewrites example StorageClass and SnapshotClass manifests with `sed`, copies them to `/tmp/csi`, and runs `make e2e-bootstrap` plus `make install-nfs-server`. `print_logs` runs example verification and driver log collection on exit.

State includes modified working-tree example manifests, `/tmp/csi` files, downloaded Kubernetes test binaries, Helm-installed cluster resources, and external test process state. Dependencies are curl, tar, sed, make, Ginkgo v1, Kubernetes external storage tests, and kubeconfig. Risks include destructive in-place `sed`, pinned old Kubernetes test version, broad focus/skip regex drift, and cleanup only printing logs. Test signal covers conformance-like external storage capabilities.
