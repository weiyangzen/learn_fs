<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/hack/orphan-mounts-stress.sh -->
# sources/control-plane/beegfs-csi-driver/hack/orphan-mounts-stress.sh

Purpose: repeated e2e stress runner for detecting orphaned BeeGFS mounts after Kubernetes volume lifecycle churn.

Important APIs and flow: creates a temp output directory, logs all script output, cleans old test namespaces, then runs 20 iterations of nondisruptive and disruptive Ginkgo e2e suites. On failure, `fail()` captures controller and node logs since script start and exits. On success, it greps controller logs for orphan-mount-related messages and removes the temp directory.

State and persistence: creates/deletes test namespaces and temporary logs under `/tmp/e2e.*`; may leave the output directory on failure for inspection.

Dependencies and integration points: requires `KUBECONFIG`, deployed driver, `ginkgo`, `kubectl`, root SSH user env, and e2e tests.

Risks and test signals: destructive namespace cleanup uses name patterns; parallel/disruptive tests can affect clusters. Test signal is either captured failure logs or clean 20-iteration completion.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/hack/orphan-mounts-stress.sh -->
