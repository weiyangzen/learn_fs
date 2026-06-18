<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/prow.sh -->
# sources/control-plane/csi-driver-smb/release-tools/prow.sh

Purpose: Large reusable Prow harness for Kubernetes CSI repositories. It builds components, runs unit tests, creates Kind clusters, installs CSI drivers/snapshot components, runs Kubernetes e2e and csi-sanity tests, collects logs, filters JUnit, and supports Cloud Build image publishing.

Important APIs/functions: Configuration is expressed through `configvar` defaults such as Go versions, Kind version/images, Kubernetes version, deployment repo/version, e2e repos, csi-sanity settings, and test focus/skip regexes. Utility functions include `get_versioned_variable`, `version_to_git`, `tests_enabled`, cluster-need predicates, `ensure_paths`, `run`, `run_with_go`, `install_kind`, `install_ginkgo`, `install_dep`, `git_checkout`, `git_clone`, `list_gates`, `list_api_groups`, `go_version_for_kubernetes`, `start_cluster`, `delete_cluster_inside_prow_job`, `find_deployment`, `install_csi_driver`, snapshot CRD/controller installers, `collect_cluster_info`, `start_loggers`, `patch_kubernetes`, `install_e2e`, `install_sanity`, `run_with_loggers`, `run_filter_junit`, `run_e2e`, `run_sanity`, `ascii_to_xml`, `make_test_to_junit`, `version_gt`, `main`, and `gcr_cloud_build`.

Control flow: Top-level config selects build/test behavior. `main` sets work paths, builds binaries/containers when enabled, runs unit tests through `make_test_to_junit`, installs Kind if needed, creates non-alpha and/or alpha clusters, installs snapshot components and the CSI driver, runs sanity and e2e suites according to configured test groups, exports/deletes clusters, merges JUnit steps, and returns accumulated failure status. `gcr_cloud_build` is a separate entrypoint for image pushes.

State and persistence behavior: Creates temporary work dirs under `$GOPATH/pkg`, binaries, checked-out repos, Kind clusters, Docker images/tags, Kubernetes resources, artifacts/logs/JUnit files, and pushed images in Cloud Build mode. It intentionally cleans Kind clusters in Prow jobs but leaves work directories for caller cleanup.

Dependencies and integration points: Integrates with Prow, Go toolchains through `GOTOOLCHAIN`, Makefile targets (`all`, `test`, `container`, `push-multiarch`), Docker, Kind, kubectl, Kubernetes source tree, Ginkgo, csi-test, CSI driver deployment scripts, external-snapshotter manifests, and `filter-junit.go`.

Risks: This is a high-blast-radius shell harness. Config parsing relies on shell word splitting and repo conventions. It downloads/builds external tools and repos dynamically. Cluster setup and test filtering are sensitive to Kubernetes/Kind version compatibility. Some paths assume Linux amd64. JUnit filtering inherits `filter-junit.go` limitations. Docker image loading parses Makefile `CMDS` with grep/sed.

Test signals: Used directly by CI jobs, so its strongest signal is Prow execution. Static release-tools checks cover shell syntax/lint/spelling/boilerplate. `verify-go-version.sh` reads its Go version.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/prow.sh -->
