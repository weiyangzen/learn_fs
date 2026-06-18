# sources/compression/xz/tests/code_coverage.sh

Purpose: convenience script to configure and run xz tests with gcov-style coverage flags, then generate HTML coverage reports with `lcov` and `genhtml`.

Important behavior: validates that `lcov` and `genhtml` exist, derives `top_srcdir` from the script location, runs `autogen.sh` if `configure` is missing, configures the current directory if no `Makefile` exists, runs `make "$@" check`, captures coverage for `src/liblzma` and `src/xz`, and writes reports under `coverage/liblzma` and `coverage/xz`.

Control flow: `set -e` makes failures abort. The configure invocation disables `xzdec`, `lzmadec`, and `lzmainfo`, disables shared libraries, enables silent rules, and appends `--coverage --no-inline -O0` to `CFLAGS` to improve coverage fidelity.

State and persistence: creates or overwrites a local `coverage/` directory, may generate configure/build files, and runs the test suite in the current build directory.

Dependencies and integration: depends on Autotools, make, lcov, genhtml, compiler coverage support, and the xz test suite. It is developer tooling, not part of installed runtime.

Risks: because it disables xzdec/lzmadec, coverage for the lightweight decoder path is intentionally absent. It removes `coverage/` unconditionally. Existing `CFLAGS` are preserved but appended, which can interact with user-supplied flags.

Test signals: successful completion prints file URLs to both HTML reports. Failures identify missing coverage tools, configure/test failures, or lcov/genhtml errors.
