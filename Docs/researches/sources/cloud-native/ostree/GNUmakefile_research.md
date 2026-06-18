<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/GNUmakefile -->
## sources/cloud-native/ostree/GNUmakefile

### Purpose
This maintainer-oriented GNU make wrapper includes generated `Makefile` rules when configured, handles version freshness for dist/install targets, and gives a clear error before configure has run.

### APIs, Types, and Control Flow
If `Makefile` exists, it exports reproducible tar options, includes `Makefile` and `cfg.mk`, sets build-aux/autoreconf defaults, computes the current git-derived version for dist/install targets, and may run `_version` to regenerate configure output. If `Makefile` does not exist, the default goal errors with instructions to run `./configure`. It also appends recursive targets and marks conflicting multi-goal recursive invocations `.NOTPARALLEL`.

### State, Dependencies, and Integration
It reads `.tarball-version`, `build-aux/git-version-gen`, `cfg.mk`, and generated automake variables. `_version` removes `autom4te.cache` and `.version`, runs autoreconf, and rebuilds `Makefile`.

### Risks and Test Signals
Version freshness logic can unexpectedly trigger autoreconf for dist-like targets, which is intended for maintainers but can surprise simple build users. Test signals are successful `make dist`, `make install` warnings when versions mismatch, and a clear abort before configure.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/GNUmakefile -->
