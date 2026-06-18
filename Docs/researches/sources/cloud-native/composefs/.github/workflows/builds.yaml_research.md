# sources/cloud-native/composefs/.github/workflows/builds.yaml

Purpose: GitHub Actions workflow that builds binary composefs artifacts across several distro container bases on every push.

Important APIs/types/functions: matrix over Ubuntu 24.04/22.04, Fedora 41, CentOS Stream 9; bootstrap git, checkout, install deps, set `SOURCE_DATE_EPOCH`, Meson configure/build/install, reproducible tar creation, artifact upload, and log upload.

Control flow: each matrix job runs in its container, installs dependencies with `hacking/installdeps.sh`, builds with FUSE disabled, captures install root as a normalized tarball, and uploads results.

State/persistence: CI artifacts `composefs-<basename>.tar` and logs.

Dependencies/integration: GitHub Actions, distro package managers, Meson, tar reproducibility options, and upload-artifact.

Risks/test signals: push-only workflow may not protect PRs; log artifact name is static `testlog-asan.txt` despite no tests. Distro image/package drift can break builds.
