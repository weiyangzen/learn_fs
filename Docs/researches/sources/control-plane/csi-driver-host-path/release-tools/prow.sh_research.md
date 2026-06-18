## sources/control-plane/csi-driver-host-path/release-tools/prow.sh

Purpose: shared CSI Prow and Cloud Build orchestration script. It builds repo binaries/images, runs unit tests, provisions kind clusters, deploys CSI drivers and snapshotter components, runs Kubernetes E2E and csi-sanity, collects artifacts, and supports multi-arch image publishing.

Important APIs are configuration helpers (`configvar`, `get_versioned_variable`, `version_to_git`), tool installers (`install_kind`, `install_ginkgo`, `install_dep`), git helpers, cluster lifecycle (`start_cluster`, `delete_cluster_inside_prow_job`), deployment helpers (`find_deployment`, `install_csi_driver`, snapshot CRD/controller installers), test runners (`run_e2e`, `run_sanity`, `make_test_to_junit`), `main`, and `gcr_cloud_build`.

State spans temp work dirs under GOPATH, ARTIFACTS, Docker images, kind clusters, kubeconfig, checked-out external repos, generated scripts/JUnit XML, and pushed multi-arch images. Dependencies include bash, Go toolchains, Docker, kind, kubectl, ginkgo, csi-sanity, GitHub/git, Kubernetes E2E, and repo Makefile conventions. Risks are high operational coupling, many version pins/defaults, fragile shell parsing and sed YAML edits, potential cluster cleanup gaps outside Prow, and broad environment assumptions. Test signal is Prow job success, JUnit artifacts, cluster logs, and Cloud Build results.
