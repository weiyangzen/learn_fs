<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/Makefile -->
## sources/compression/zstd/tests/gzip/Makefile

Purpose: Drives zstd's imported gzip compatibility regression tests. It builds the zstd program, symlinks it as `gzip`, prepends the local directory to `PATH`, and runs selected gzip shell tests through the bundled Automake-style `test-driver.sh`.

Important APIs and targets: `PRGDIR = ../../programs` points at the zstd CLI build directory. `all` depends on individual `test-*` targets for gzip behavior regressions; `test-gzip-env` is present but commented out from the default list. `zstd` invokes `$(MAKE) -C $(PRGDIR) zstd`, creates `gzip -> ../../programs/zstd`, prints `PATH`, and runs `gzip --version`. `clean` delegates to the programs clean target and removes `.trs` and `.log` files.

Control flow: On supported Unix-like systems, the pattern rule `test-%: zstd` first ensures the symlinked gzip-compatible zstd binary is built, then executes `./test-driver.sh` with test name, log path, result path, hard-error handling, and the corresponding `./$*.sh` script.

State and persistence: Writes the local `gzip` symlink and per-test `.log`/`.trs` files. `clean` removes logs and delegates binary cleanup. No source files are modified.

Dependencies and integration points: Integrates zstd's `programs/zstd` with GNU gzip test scripts by relying on argv name/format compatibility. It depends on POSIX `make`, `uname`, `ln -sf`, shell execution, and the local `test-driver.sh`. The OS filter limits execution to Linux, Darwin, GNU variants, FreeBSD, DragonFly, and NetBSD-style environments.

Risks: Because `PATH` starts with `.`, any helper script or symlink in the test directory can shadow host tools. The OS filter omits unsupported platforms instead of failing, so coverage is conditional. The commented `test-gzip-env` means GZIP environment variable behavior may not run under the default `all` target.

Test signals: A successful run emits `PASS` lines from `test-driver.sh` and ends with `Testing completed`. Expected artifacts include one `.log` and `.trs` per `test-*` target.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/Makefile -->
