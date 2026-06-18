<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/flatpak.sh -->
## sources/cloud-native/ostree/ci/flatpak.sh

### Purpose
This integration script builds Flatpak against the just-built OSTree and runs Flatpak's test suite to catch API or behavior regressions.

### APIs, Types, and Control Flow
It pins `FLATPAK_TAG=1.4.1`, builds OSTree through `ci/build.sh` without installing first, clones Flatpak recursively at that tag into a tempdir, applies an OSTree GPG error compatibility patch, installs Flatpak build dependencies, installs the just-built OSTree over the packaged version with `make install`, builds Flatpak using the shared `build` helper, traps cleanup to move `test-suite.log` back to the OSTree checkout, and runs `make -j 8 check`.

### State, Dependencies, and Integration
It writes a temp Flatpak checkout, installs packages and OSTree into the CI system, and captures Flatpak test logs. It depends on network access to GitHub, distro package managers, Flatpak build dependencies, and the repository patch file.

### Risks and Test Signals
The pinned old Flatpak tag is intentional for API compatibility but may become harder to build on newer distros. Installing OSTree over system packages is CI-oriented. Test signal is Flatpak's automake test suite passing with this OSTree build.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/flatpak.sh -->
