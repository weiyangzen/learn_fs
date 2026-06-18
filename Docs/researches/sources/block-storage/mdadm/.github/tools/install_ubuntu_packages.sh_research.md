# File Research: sources/block-storage/mdadm/.github/tools/install_ubuntu_packages.sh

## Purpose
This helper script prepares Ubuntu GitHub Actions runners for the mdadm review build matrix.

## Behavior
- Reads `VERSION_CODENAME` from `/etc/os-release`.
- Adds the matching Ubuntu `main universe` archive repository for `amd64`.
- Installs the GCC version passed as the first argument, using package name `gcc-$1`.
- Installs common build/review dependencies: `make`, `gcc`, `libudev-dev`, and `devscripts`.
- Uses `--no-upgrade`, `--no-install-recommends`, and `--no-install-suggests` to limit package churn.

## Integration Notes
`review.yml` calls this script for each compiler version in the matrix. `devscripts` supplies tools such as `hardening-check`, which the workflow runs after compilation.

## Risks and Maintenance Notes
The script assumes an Ubuntu-like environment with `add-apt-repository`, `sudo`, and `apt-get`. It interpolates the first argument into a package name without validation; in this controlled workflow context the input is the fixed compiler matrix.
