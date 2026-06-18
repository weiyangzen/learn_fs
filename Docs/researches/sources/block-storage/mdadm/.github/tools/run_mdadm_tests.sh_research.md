# File Research: sources/block-storage/mdadm/.github/tools/run_mdadm_tests.sh

## Purpose
This helper script builds, installs, and runs the mdadm test suite inside the self-hosted/Vagrant test environment.

## Behavior
- Runs `sudo make clean`, then builds with `sudo make -j$(nproc)`.
- Exits immediately with an error message if build or install fails.
- Installs with `sudo make install`.
- Stops active md arrays with `sudo mdadm -Ss`.
- Runs `sudo ./test setup`.
- Executes the test harness with skipped known-problem and expensive modes: `--skip-broken`, `--no-error`, `--disable-integrity`, `--disable-multipath`, `--disable-linear`, `--keep-going`, and `--skip-bigcase`.
- Captures the test return code, runs `sudo ./test cleanup`, and exits with the original test status.

## Integration Notes
`.github/workflows/tests.yml` invokes this script through `vagrant ssh` from a self-hosted runner. The script intentionally cleans up after the test run even when tests fail.

## Risks and Maintenance Notes
The script uses privileged build, install, array stop, setup, test, and cleanup commands. It is appropriate for disposable CI VMs, not a developer workstation with important active md arrays.
