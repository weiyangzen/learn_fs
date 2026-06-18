# File Research: sources/block-storage/mdadm/.github/workflows/mdadm-test.yml

## Purpose
This GitHub Actions workflow builds mdadm and runs the test harness on GitHub-hosted Ubuntu runners.

## Behavior
- Named `mdadm test`.
- Runs on pushes to branch `test_on_push`, pull requests to branch `test_on_pr`, and manual `workflow_dispatch`.
- Path filters include top-level C and header files, `tests/*`, `test`, and this workflow file.
- Checks out the repository with full history.
- Installs `make`, `gcc`, and `libudev-dev`.
- Builds with `make -j$(nproc) BINDIR=/usr/sbin`.
- Installs mdadm binaries with `sudo make BINDIR=/usr/sbin install-bin`.
- Prints `mdadm --version`.
- Rewrites the test harness `targetdir` from `/var/tmp` to `/mnt/tmp`, creates that directory, and runs tests under `sudo`.
- Uploads `/mnt/tmp/*.log` as `mdadm-failed-test-logs`.
- Runs tests with `continue-on-error: true`, then explicitly fails the job if the test step outcome was not success.

## Integration Notes
This workflow is separate from the main `tests.yml` self-hosted path. It gives a GitHub-hosted smoke/integration test route with reduced test modes: integrity, multipath, and linear are disabled.

## Risks and Maintenance Notes
The branch filters are nonstandard (`test_on_push`, `test_on_pr`), so the workflow does not run for ordinary branches unless repository policy uses those branch names. Artifact upload runs unconditionally after the test step, so missing logs may depend on action behavior.
