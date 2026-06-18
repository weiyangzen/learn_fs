<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/Makefile -->
# sources/control-plane/ceph-csi/Makefile

Purpose: main build, test, lint, module, container, image, deploy-generation, and e2e entrypoint for Ceph CSI.
Important targets: `test`, `go-test`, `go-test-api`, `mod-check`, `go-lint`, `lint-extras`, `commitlint`, `cephcsi`, `e2e.test`, `generate-deploy`, `run-e2e`, `containerized-build`, `containerized-test`, `image-cephcsi`, manifest push targets, and `clean`.
Control flow/state: discovers podman/docker, sets CPUSET support, loads `build.env` for versions/timeouts, builds with vendor mode and LDFLAGS carrying git commit/driver version, creates cached `.devel-container-id` and `.test-container-id`, and fails if module/deploy generation dirties git state.
Dependencies/integration: root of the GitHub Actions workflows, deploy generator, scripts directory, containerfiles, Go modules in root/e2e/api/actions/retest, and Quay image naming.
Risks/test signals: container cache IDs are local mutable state; `mod-check` rewrites vendor before checking status; UID/cgroup cpuset detection can differ by environment; Docker is forced for some multi-arch paths. CI statuses are direct Makefile target outcomes.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/Makefile -->
