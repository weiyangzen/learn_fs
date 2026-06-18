<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/ci-release-build.sh -->
## sources/cloud-native/ostree/ci/ci-release-build.sh

### Purpose
This script verifies that release-build mode in `configure.ac` matches the commit title and symbol-file state.

### APIs, Types, and Control Flow
It writes the selected commit message to `log.txt`, removes temporary files on exit, and checks `configure.ac` for `is_release_build=yes`. In release mode it builds a small `version.m4` file from `m4_define` version macros, evaluates `package_version`, requires the commit message to start with `Release $V`, and ensures `src/libostree/libostree-devel.sym` no longer references `LIBOSTREE_$V`. In non-release mode it rejects commit titles that look like releases.

### State, Dependencies, and Integration
It reads git commit messages, `configure.ac`, and symbol files, and writes temporary `version.m4`/`log.txt`. It integrates with `release.yml`.

### Risks and Test Signals
Parsing relies on m4 macro layout in `configure.ac` and commit title conventions. Test signal is release PR CI confirming release flag/version/title/symbol consistency at both HEAD and HEAD parent.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/ci-release-build.sh -->
