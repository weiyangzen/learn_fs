# sources/control-plane/csi-driver-iscsi/release-tools/prow.sh

Purpose: shared Prow and Cloud Build orchestration library for Kubernetes CSI repositories, covering build, unit tests, kind cluster setup, CSI driver deployment, Kubernetes E2E, CSI sanity, JUnit generation, snapshot controller setup, and multi-arch image publishing.

Important APIs and types: `configvar` declares overridable defaults for Go versions, build platforms, kind/Kubernetes versions, hostpath driver deployment, sidecar E2E, sanity, feature gates, and test selection. Major functions include `ensure_paths`, `run_with_go`, `install_kind`, `install_ginkgo`, `git_checkout`, `git_clone`, `start_cluster`, `install_csi_driver`, `install_snapshot_crds`, `install_snapshot_controller`, `collect_cluster_info`, `start_loggers`, `patch_kubernetes`, `install_e2e`, `install_sanity`, `run_e2e`, `run_sanity`, `make_test_to_junit`, `main`, and `gcr_cloud_build`.

Control flow: repos source this file after overriding variables. `main` creates work directories, builds binaries and containers, runs unit tests as JUnit, installs kind if needed, creates non-alpha and optional alpha clusters, applies snapshot CRDs/controllers, deploys the CSI driver, runs sanity and E2E subsets selected by focus/skip regexes, collects logs, tears down clusters, and merges JUnit output. `gcr_cloud_build` configures Docker auth/QEMU and runs `make push-multiarch`.

State and persistence: creates temporary work under GOPATH, writes artifacts/JUnit/log files, creates and deletes kind clusters, loads local Docker images, patches checked-out Kubernetes manifests in the work tree for canary tests, and pushes images in Cloud Build mode.

Dependencies and integration: integrates with Go toolchains via `GOTOOLCHAIN`, kind, Docker, kubectl, ginkgo, Kubernetes source builds, csi-test, external-snapshotter manifests, repo Makefiles, Prow artifact conventions, and Cloud Build/gcloud.

Risks: large shell surface with many environment contracts. Some defaults can become stale as Kubernetes, sidecars, and kind evolve. Many operations depend on network access and mutable external repos. It uses `git clean -fdx` inside its own checked-out work paths. Image and deployment override generation depends on Makefile `CMDS` parsing.

Test signals: Prow job success, unit JUnit, E2E JUnit, sanity JUnit, kind logs, cluster info artifacts, and successful multi-arch image pushes.
