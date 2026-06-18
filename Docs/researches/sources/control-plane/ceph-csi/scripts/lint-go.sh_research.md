<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/lint-go.sh -->
## sources/control-plane/ceph-csi/scripts/lint-go.sh

Purpose: runs Go linting through `golangci-lint`.

Control flow: enables pipefail, checks for executable `golangci-lint`, then runs `golangci-lint --config=scripts/golangci.yml run ./... -v "$@"`; otherwise prints a warning and exits successfully.

State and dependencies: no state; requires generated `scripts/golangci.yml` and golangci-lint for actual enforcement.

Integration points: local/CI Go lint entrypoint.

Risks: missing golangci-lint only warns, so enforcement depends on CI image having the tool. Config path is generated from `golangci.yml.in`.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/lint-go.sh -->
