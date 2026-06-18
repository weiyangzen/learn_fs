# sources/control-plane/csi-driver-nfs/release-tools/prow.sh

Purpose: shared Kubernetes CSI Prow orchestration script for building components, creating kind clusters, deploying CSI drivers, running unit/E2E/sanity tests, collecting artifacts, merging JUnit output, and supporting GCR Cloud Build image pushes.

Important APIs and functions: `configvar`, `get_versioned_variable`, `version_to_git`, test selectors (`tests_enabled`, `sanity_enabled`, `tests_need_kind`), `ensure_paths`, `run`, `run_with_go`, installers for kind/ginkgo/dep/e2e/sanity, `git_checkout`, `git_clone`, `go_version_for_kubernetes`, `start_cluster`, `delete_cluster_inside_prow_job`, `find_deployment`, `install_csi_driver`, `install_snapshot_crds`, `install_snapshot_controller`, `collect_cluster_info`, `start_loggers`, `patch_kubernetes`, `run_e2e`, `run_sanity`, `make_test_to_junit`, `version_gt`, `main`, and `gcr_cloud_build`.

Control flow: the script initializes many configurable `CSI_PROW_*` defaults, including Go versions, Kubernetes/kind versions and images, driver deployment source, E2E focus/skip regexes, snapshotter version, and test matrix. `main` builds binaries/images with the configured Go toolchain, optionally runs unit tests and converts make output to JUnit, creates kind clusters when needed, installs snapshot CRDs/controller, deploys either locally built images or external driver deployments, runs sanity and E2E tests by focus groups, exports logs on failures, deletes clusters in Prow, and merges JUnit outputs through `filter-junit.go`. `gcr_cloud_build` handles image-push setup for Cloud Build.

State and persistence behavior: creates temporary work directories under `$GOPATH/pkg`, installs tools into a temp bin directory, clones repositories, builds images, tags and side-loads Docker images, creates/deletes kind clusters, writes kubeconfig/artifacts/JUnit files, and can push multi-arch images in Cloud Build. It does not itself commit repository changes.

Dependencies and integration points: central integration point for Makefiles, Docker, kind, kubectl, ginkgo, Kubernetes E2E tests, csi-test sanity, external-snapshotter CRDs/controller, git/GitHub repos, Cloud Build, and release-tools `filter-junit.go`. Consuming repos customize behavior through environment variables or wrapper `.prow.sh` files.

Risks: large shell surface with many external tool and network dependencies. Numerous values are parsed with grep/sed and word splitting. Cluster and image behavior depends on version compatibility among Kubernetes, kind, CSI sidecars, and deployment YAML. Some failures are fatal, while unit/E2E failures accumulate into a return code. Artifact ordering and cleanup can vary by Prow environment.

Test signals: no standalone unit tests for the script in this subset. Its signal is end-to-end Prow/Cloud Build execution: successful builds, unit test JUnit, E2E/sanity JUnit, cluster logs, and final merged JUnit.
