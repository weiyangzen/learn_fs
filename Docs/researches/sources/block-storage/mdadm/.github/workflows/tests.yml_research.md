# File Research: sources/block-storage/mdadm/.github/workflows/tests.yml

## Purpose
This workflow defines the heavier upstream mdadm test run on self-hosted infrastructure.

## Behavior
- Runs on pull requests touching top-level C/header files, tests, `test`, and GitHub workflow/tooling files.
- The main `upstream_tests` job is currently disabled with `if: ${{ github.repository == 'disabled' }}` and a comment that Intel hosted runners are down.
- When enabled, it runs on a self-hosted runner with a 150-minute timeout.
- Uses Vagrant to restore a clean VM snapshot, start the VM, set UTC time, restart time synchronization, and print the kernel version.
- Exports `RUNNER_NAME` into the GitHub environment.
- Runs `.github/tools/run_mdadm_tests.sh` inside the VM at `/home/vagrant/host/mdadm`.
- On failure, moves `/var/tmp/*.log` from the VM into host logs and uploads artifacts from runner-specific paths for `inspur5` or `inspur5-2`.
- Cleans copied logs after upload and explicitly fails the job if testing failed.
- A dependent `cleanup` job halts the VM with `vagrant halt`.

## Integration Notes
This workflow is tied to specific self-hosted runner filesystem layouts and Vagrant snapshots. It is the CI path that exercises the project’s privileged test harness in a VM rather than directly on the GitHub runner.

## Risks and Maintenance Notes
The main job is disabled by an always-false repository check, which also means the dependent cleanup job will not normally run. Runner names and artifact paths are hard-coded, so adding or renaming self-hosted runners requires workflow edits.
