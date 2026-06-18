# sources/control-plane/mayastor/.github/workflows/fossa.yml

## Purpose
Runs FOSSA license/security scanning on `develop` and `release/**` pushes.

## Important Jobs and Steps
Single `fossa-scan` job on `ubuntu-latest`, checkout with recursive submodules, then `fossas/fossa-action@v1.4.0` using `FOSSA_API_KEY`.

## Control Flow
Push trigger starts the scan. The action handles dependency discovery and reporting to FOSSA.

## State and Persistence
No repo writes. External FOSSA project state is updated.

## Dependencies and Integration Points
Requires FOSSA secret and action availability. Recursive submodules are included in scan context.

## Risks
Scan coverage depends on FOSSA action support for Nix/Rust/submodules. Secret absence fails the workflow. Only push branches are scanned, not every PR.

## Test Signals
Successful FOSSA action run and updated FOSSA report. Branch protection may consume this if configured externally.
