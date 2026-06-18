# sources/cloud-native/soci-snapshotter/.github/workflows/build.yml

Purpose: main build, unit, root-required, and integration CI workflow for SOCI Snapshotter.

Important APIs/types/functions: reusable `setup.yml` runner matrix; jobs `test`, `test-root`, and `integration`; Go versions `1.25.11` and `1.26.4`; containerd versions `1.7.32`, `2.0.9`, `2.2.4`, and `2.3.1`; Make targets `make`, `test-with-coverage`, `integration-with-coverage`, coverage display.

Control flow: triggered on main/release pushes and code-relevant PRs. Unit tests run across available runner OS labels and two Go versions. Root test runs snapshot package with `sudo -E`. Integration tests run a larger matrix over Go and containerd versions, installing gotestsum and platform-specific zlib static dependencies.

State and persistence: produces coverage data in workspace; no artifact upload here.

Dependencies/integration: depends on setup runner workflow, Makefile targets, Docker/containerd integration environment, and CodeBuild runners for awslabs.

Risks: high matrix size can be expensive. `SKIP_SYSTEMD_TESTS` is set only for `ubuntu-x86`. Future Go/containerd version changes require updates across workflows.

Test signals: this is the primary correctness gate for library, CLI, snapshot root tests, and integration behavior.
