# sources/distributed-fs/lizardfs/utils/coverage.sh

Purpose: test coverage helper for LizardFS CMake builds. It prepares build directories for coverage data written by tests running under different UIDs and generates filtered HTML coverage reports.

Important commands/control flow: the script expects `prepare <build-dir>` or `generate-html <build-dir> <out-dir>`. It first verifies `<build-dir>/CMakeCache.txt`. `prepare` sets every directory in the build tree writable by all users and removes existing `*.gcda` files. `generate-html` creates the output directory, captures with `lcov --capture --directory .`, filters out system headers, `external`, `tests`, `utils`, and `devtools`, runs `genhtml`, then removes temporary `cov.raw` and `cov.info`.

State and persistence: mutates permissions under the build directory, deletes old coverage counters, and creates an HTML report in the requested output directory. Temporary coverage files are created in the caller's working directory, not necessarily inside `builddir`.

Dependencies/integration: depends on Bash, `find`, `xargs`, `lcov`, and `genhtml`; expects CMake/gcov-style artifacts. It is part of developer/test tooling rather than runtime.

Risks and test signals: `command=$1` and `builddir=$2` are read before argument validation, so `set -u` is not enabled until command branches. `xargs` without `-r` may invoke commands with empty input on some platforms. Coverage capture uses `--directory .`, so callers must run it from a meaningful build context. Test signals are prepare on populated and empty build trees, report generation with filtering, and permission handling when tests run under another UID.
