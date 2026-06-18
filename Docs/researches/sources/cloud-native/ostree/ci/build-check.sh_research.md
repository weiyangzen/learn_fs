<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/build-check.sh -->
## sources/cloud-native/ostree/ci/build-check.sh

### Purpose
This CI script installs dependencies, builds OSTree, runs unit and installed tests, and optionally performs a clang rebuild for stricter warnings.

### APIs, Types, and Control Flow
It sources `libbuild.sh`, runs `ci/build.sh`, creates a results directory, executes `make check`, moves `test-suite.log` and `config.log`, runs `make install`, then if clang is available and not blocked by a GLib macro issue, cleans the tree, switches `CC=clang`, and rebuilds. A helper copies logs and GNOME desktop testing results to `$ARTIFACTS` or the repo root. If `gnome-desktop-testing-runner` exists, it clones/builds a newer runner, installs it, traps artifact copy, and runs installed tests.

### State, Dependencies, and Integration
It modifies build/install outputs, may `git clean -dfx` the repo and submodules, and writes artifact logs. It depends on `libbuild.sh`, clang, git, make, and optionally GNOME desktop testing.

### Risks and Test Signals
The destructive clean is appropriate for CI but unsafe for dirty local work unless intentional. Network clone of gnome-desktop-testing can fail. Test signals are unit `make check`, install success, clang build, and installed-test runner results.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/build-check.sh -->
