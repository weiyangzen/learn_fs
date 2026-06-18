# File Research: sources/block-storage/mdadm/.github/workflows/review.yml

## Purpose
This workflow performs pull-request review checks: compiler matrix builds, hardening checks, and checkpatch review.

## Behavior
- Runs on every pull request.
- Sets `cflags: -Werror` in the workflow environment.
- The `make` job runs on `ubuntu-24.04` across GCC versions 9 through 14.
- For each compiler version it installs packages through `.github/tools/install_ubuntu_packages.sh`.
- Verifies the selected compiler with `gcc-N --version`.
- Builds repeatedly with different `CXFLAGS`: `-DEBUG`, `-DEBIAN`, `-USE_PTHREADS`, and `-DNO_LIBUDEV`, cleaning between variants.
- Performs a normal build, then runs `hardening-check mdadm` and `hardening-check mdmon`.
- The `checkpatch` job checks out the pull request head SHA with full history, moves `.github/tools/.checkpatch.conf` to the repository root, and runs `webispy/checkpatch-action@v9`.

## Integration Notes
The build matrix exercises feature/preprocessor combinations that affect mdadm portability and packaging. `devscripts` from the install helper supplies `hardening-check`.

## Risks and Maintenance Notes
The `CXFLAGS=-DEBUG`, `CXFLAGS=-DEBIAN`, and `CXFLAGS=-USE_PTHREADS` values are notable because typical C preprocessor defines use `-D...`; this may be intentional project makefile syntax or a latent workflow issue. The workflow depends on old GCC packages being installable for the current Ubuntu codename.
