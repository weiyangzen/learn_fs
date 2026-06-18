# sources/control-plane/mayastor/.github/workflows/bdd.yml

## Purpose
Reusable GitHub Actions workflow for Mayastor BDD tests.

## Important Jobs and Steps
`bdd-tests` runs on `cncf-ubuntu-16-64-x86` with read contents and OIDC token permissions. It checks out submodules, installs Nix, injects GitHub token/trusted users into Nix config, pre-populates `nix-shell`, uses Rust cache, builds binaries with `io-engine-testing`, prepares kernel modules and hugepages, configures Docker journald logging, sets up Python venv, runs `./scripts/pytest-tests.sh`, publishes pytest report, collects failure artifacts with `ci-report.sh`, checks coredumps, and cleans Python tests.

## Control Flow
Triggered only by `workflow_call`, typically from PR/bors CI. Cleanup and coredump checks run with `if: always()`, while reports/artifacts run on failure or cancellation.

## State and Persistence
Creates build outputs, Python reports, Docker state, kernel module state, hugepage settings, and uploaded artifacts. It does not persist repo changes.

## Dependencies and Integration Points
Depends on custom CNCF runner capabilities, Nix shell, SPDK submodule Nix sources, Docker, kernel modules `nvme_tcp`, `nbd`, `nvme_rdma`, gdb, and test scripts. Integrates into `pr-ci.yml`.

## Risks
Runner-specific kernel/module requirements make portability low. The workflow mutates `/etc/nix/nix.conf` and Docker daemon config. Empty GitHub token input to Nix install may be intentional but fragile. Heavy BDD cleanup must remain reliable to avoid contaminating shared runners.

## Test Signals
Primary signal is `pytest-tests.sh` xunit report plus coredump absence. Failure artifact `ci-report-bdd` is the diagnostic package.
