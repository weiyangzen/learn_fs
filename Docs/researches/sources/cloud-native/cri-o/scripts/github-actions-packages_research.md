# sources/cloud-native/cri-o/scripts/github-actions-packages

This Bash script installs Ubuntu packages required by CRI-O GitHub Actions jobs. It sources `/etc/os-release`, constructs an OpenSUSE CRIU repository URL for the Ubuntu version, adds its key and apt source, updates package indexes, and installs build/runtime dependencies such as conmon, criu, development headers, rust/cargo, lld, make, socat, and wget.

There are no functions; execution is linear with `set -euo pipefail`. State changes are system-wide: apt keys/sources, package cache, and installed packages. Dependencies include sudo, curl, apt-key, apt, tee, and network access to the CRIU repository. Integration is CI setup for tests that need CRIU, conmon, storage libraries, seccomp, AppArmor, and build tools.

Risks include deprecated `apt-key`, repository availability, unquoted variable expansion for the repository URL, broad system mutation on the runner, and package drift over time. Test signal is operational rather than unit-tested; failures surface in CI setup.
