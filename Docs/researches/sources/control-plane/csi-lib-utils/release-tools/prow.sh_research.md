# sources/control-plane/csi-lib-utils/release-tools/prow.sh

## Purpose

`prow.sh` is the shared CI and release-tool driver imported by Kubernetes CSI repositories. It builds components, runs unit and E2E tests in KinD, installs CSI drivers and snapshot components, runs csi-sanity, produces JUnit artifacts, and supports Cloud Build multiarch image publishing.

## Important APIs and Control Flow

Configuration is centralized through `configvar`, which sets default environment variables while allowing repo-level `.prow.sh` or job settings to override them. Helpers include `tests_enabled`, `version_to_git`, `get_versioned_variable`, `regex_join`, `ensure_paths`, `run`, `die`, and `run_with_go`. Tool installers fetch or build `kind`, `ginkgo`, `dep`, Kubernetes E2E binaries, and csi-sanity. Git helpers check out or clone external repositories.

Cluster flow uses `start_cluster` to choose or build a KinD node image, write `kind-config.yaml`, and create a two-worker cluster. Driver setup uses `find_deployment` and `install_csi_driver`, optionally loading locally built images and overriding stable/canary tags. Snapshot setup installs CRDs and snapshot-controller manifests, with special handling for external-snapshotter PRs and canary images. Test flow runs unit `make test` through `make_test_to_junit`, E2E suites through `run_e2e`, csi-sanity through `run_sanity`, and final JUnit merging through `run_filter_junit`. `main` coordinates all of this and preserves a nonzero return for failed nonfatal tests. `gcr_cloud_build` is the Cloud Build entrypoint for multiarch pushes.

## State, Dependencies, and Integration

The script creates temporary work directories under `$GOPATH/pkg`, artifact directories, KinD clusters, Docker images/tags, generated helper scripts, kubeconfig state, fetched repos, and JUnit/log artifacts. It depends on bash, Go with toolchain support, Docker, kind, kubectl, git, curl, make, ginkgo, csi-sanity, Kubernetes source, CSI hostpath/snapshotter repos, and repository Makefile conventions. It is sourced by component `.prow.sh` files and by Cloud Build wrappers.

## Risks and Test Signals

This file is high blast-radius: environment defaults, version matrices, image tags, feature gates, and regex selections define CI behavior across many repositories. Shell parsing of Makefile `CMDS`, deployment YAML image rewriting, branch/tag checkout logic, and JUnit XML generation are fragile areas. The script intentionally continues from unit failures to E2E tests but returns failure at the end. Test signals are Prow logs, JUnit artifacts, KinD cluster logs, csi-sanity output, `make` results, and Cloud Build/image push results.
